# Figura edu-01 — vent'anni di miglioramento che non è mai diventato posizione.
# Claim del thread educazione (invariato): fra 1991 e 2011 Bagheria migliora su tutti e
# cinque gli indicatori e su tutti e cinque arretra nella graduatoria dei 390 comuni.
#
# PERCHÉ QUESTA FORMA E NON DUE PANNELLI DI BARRE (figures/edu/02).
# Il claim è appaiato — "migliora E arretra" — e le barre lo spezzavano in due pannelli di
# variazioni che l'occhio deve riappaiare leggendo le etichette. Due difetti concreti:
#   1. una barra di VARIAZIONE nasconde da dove si parte. +22,3 p.p. sul diploma e +0,4
#      sull'occupazione sono la stessa grammatica visiva, ma il secondo parte da 19,6 e
#      arriva a 20,0: la barra dice "poco", il dumbbell dice "fermo".
#   2. il percentile È una posizione: codificarlo come lunghezza di barra costringe a
#      immaginare la classifica invece di vederla. Come slopegraph la posizione sta
#      sull'asse, e il fatto che tutte e cinque le linee scendano diventa una figura sola
#      invece di cinque segni meno da confrontare.
# Il pannello destro guadagna anche il 2001, che le barre di variazione 1991-2011
# buttavano via: l'arretramento non è un salto fra due censimenti, è una discesa continua.
#
# Colore: nessuna scala categorica. Le cinque linee sono lo stesso soggetto (Bagheria) su
# indicatori diversi, e sono etichettate agli estremi — un colore per linea aggiungerebbe
# una chiave da imparare senza aggiungere informazione. Vermiglio perché il soggetto è
# Bagheria, come in tutta la cartella.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 30

# Il verso di ogni indicatore ("alto = favorevole" / "alto = sfavorevole") arriva dalla
# pipeline: è una scelta interpretativa già fissata, qui non si rifà.
storia <- read_csv(file.path(PROCESSED, "edu_historical_bagheria.csv"),
                   show_col_types = FALSE)
cambio <- read_csv(file.path(PROCESSED, "edu_historical_change_1991_2011.csv"),
                   show_col_types = FALSE)

# I cinque indicatori del claim sono quelli della tavola di variazione, non tutti quelli
# disponibili: `edu_historical_bagheria.csv` porta anche I8 (almeno licenza media 15-19),
# che la tavola di variazione non include. Filtrare sulla tavola tiene la figura sullo
# stesso perimetro dell'affermazione: cinque indicatori, cinque volte lo stesso esito.
INDICATORI <- cambio$indicatore
CENSIMENTI <- c(1991, 2001, 2011)

dati <- storia |>
  filter(indicatore %in% INDICATORI) |>
  inner_join(select(cambio, indicatore, metrica), by = "indicatore") |>
  mutate(
    sfavorevole = direzione == "alto = sfavorevole",
    # Percentile FAVOREVOLE: sugli indicatori dove salire è peggio si ribalta, così i
    # cinque assi hanno lo stesso verso e "in basso" significa sempre "sta indietro".
    # Senza il ribaltamento, due linee salirebbero e tre scenderebbero dicendo la stessa
    # identica cosa, e la figura smentirebbe il proprio titolo.
    percentile_fav = ifelse(sfavorevole, 100 - percentile_sicilia, percentile_sicilia))

stopifnot(nrow(dati) == length(INDICATORI) * length(CENSIMENTI),
          setequal(dati$anno, CENSIMENTI))

# Il claim in una riga: tutti migliorano, nessuno converge. Se la pipeline cambiasse
# idea su una sola riga, il titolo qui sotto smetterebbe di essere vero e la figura
# deve fermarsi invece di raccontarlo lo stesso.
stopifnot(all(cambio$miglioramento_assoluto), !any(cambio$convergenza_relativa))
N <- nrow(cambio)

# L'ordine delle righe lo fissa la posizione raggiunta nel 2011, dal meglio al peggio.
# Vale per entrambi i pannelli: a sinistra è l'ordine delle righe, a destra l'ordine in
# cui le linee arrivano al 2011. Le due liste di etichette si leggono in parallelo.
ordine <- dati |>
  filter(anno == 2011) |>
  arrange(desc(percentile_fav)) |>
  pull(metrica)

dati <- mutate(dati, metrica = factor(metrica, levels = rev(ordine)))

# --- pannello A: i livelli, 1991 -> 2011 ---------------------------------------------
# Un asse solo per tutti e cinque: i valori stanno fra 6,4% e 42,9%, quindi le lunghezze
# sono confrontabili senza trucchi di scala.
livelli <- dati |>
  select(metrica, sfavorevole, anno, valore) |>
  pivot_wider(names_from = anno, values_from = valore, names_prefix = "a") |>
  arrange(metrica)

# La freccia punta dove sta il 2011; il verso "buono" cambia per indicatore e si dice
# nell'etichetta di riga, non nel colore: sono cinque miglioramenti su cinque, un colore
# che codifica una costante è rumore.
livelli <- mutate(livelli, etichetta_verso = ifelse(sfavorevole, "↓ meglio", "↑ meglio"))

ETICHETTE_RIGA <- setNames(paste0(livelli$metrica, "\n", livelli$etichetta_verso),
                           as.character(livelli$metrica))

pannello_livelli <- ggplot(livelli, aes(y = metrica)) +
  geom_segment(aes(x = a1991, xend = a2011), linewidth = 2.4, colour = "grey85",
               lineend = "round") +
  # Il 2001 come tacca sul segmento: dice che il percorso è graduale senza rubare
  # l'attenzione ai due estremi, che sono quelli che il claim confronta.
  geom_point(aes(x = a2001), size = 2.1, colour = "grey62") +
  geom_point(aes(x = a1991), size = 4.2, shape = 21, stroke = 1.1, colour = "grey55",
             fill = "white") +
  geom_point(aes(x = a2011), size = 4.6, colour = COLORI_TERRITORIO[["Bagheria"]]) +
  geom_text(aes(x = pmin(a1991, a2011), label = virgola(pmin(a1991, a2011), 1, "%")),
            hjust = 1, nudge_x = -1.4, size = 3.1, colour = "grey45") +
  geom_text(aes(x = pmax(a1991, a2011), label = virgola(pmax(a1991, a2011), 1, "%")),
            hjust = 0, nudge_x = 1.4, size = 3.1, fontface = "bold", colour = "grey20") +
  scale_x_continuous(limits = c(-2, 54), breaks = seq(0, 40, 10),
                     labels = function(x) virgola(x, 0, "%"),
                     expand = expansion(mult = 0)) +
  scale_y_discrete(labels = ETICHETTE_RIGA) +
  labs(subtitle = paste0("I livelli migliorano, tutti e ", N, "\n",
                         "quota osservata a Bagheria: cerchio vuoto 1991, tacca 2001, pieno 2011"),
       x = "quota della popolazione di riferimento", y = NULL)

# --- pannello B: la posizione fra i 390 comuni siciliani -----------------------------
# Le etichette di fine linea si scostano quanto basta per non sovrapporsi: due indicatori
# arrivano al 2011 a un punto percentile di distanza (occupazione 13°, NEET 12°) e le due
# scritte finivano una sull'altra. Lo scostamento tocca SOLO il testo — i pallini restano
# sul valore vero — ed è dichiarato in caption.
GAP_ETICHETTE <- 5.4   # unità di percentile fra due etichette adiacenti

ultimi <- filter(dati, anno == 2011) |> mutate(y_etichetta = scosta_etichette(percentile_fav, GAP_ETICHETTE))
primi <- filter(dati, anno == 1991) |> mutate(y_etichetta = scosta_etichette(percentile_fav, GAP_ETICHETTE))

pannello_posizione <- ggplot(dati, aes(anno, percentile_fav, group = metrica)) +
  # La mediana regionale: la riga che dice "metà dell'isola sta sopra, metà sotto".
  geom_hline(yintercept = 50, linewidth = 0.5, colour = "grey65", linetype = "22") +
  annotate("text", x = 2012.4, y = 50, hjust = 0, vjust = 0.5, size = 2.9,
           colour = "grey45", label = "mediana\nregionale") +
  geom_line(linewidth = 1.05, colour = COLORI_TERRITORIO[["Bagheria"]], alpha = 0.85) +
  geom_point(size = 2.4, colour = COLORI_TERRITORIO[["Bagheria"]]) +
  geom_text(data = primi, aes(y = y_etichetta, label = virgola(percentile_fav, 0, "°")),
            hjust = 1, nudge_x = -1.4, size = 3.1, colour = "grey45") +
  geom_text(data = ultimi,
            aes(y = y_etichetta,
                label = paste0(virgola(percentile_fav, 0, "°"), "  ", metrica)),
            hjust = 0, nudge_x = 1.4, size = 3.3, fontface = "bold", colour = "grey20") +
  scale_x_continuous(breaks = CENSIMENTI, limits = c(1984, 2049),
                     expand = expansion(mult = 0)) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 25),
                     labels = function(x) virgola(x, 0, "°")) +
  labs(subtitle = paste0("E la posizione peggiora, tutte e ", N, "\n",
                         "percentile favorevole fra i 390 comuni siciliani: in alto = davanti"),
       x = NULL, y = "percentile favorevole")

figura <- (pannello_livelli | pannello_posizione) +
  plot_layout(widths = c(1, 1.12)) +
  plot_annotation(
    title = paste0("Bagheria migliora su tutti e ", N,
                   " gli indicatori educativi, e su tutti e ", N, " scivola indietro"),
    subtitle = sommario(paste0(
      "Tre censimenti, 1991-2011. A sinistra quanto è cambiata la quota; a destra dove si colloca Bagheria fra i 390 comuni siciliani, ribaltando il percentile\n",
      "dove salire è peggio, così che in alto significhi sempre \"davanti\". Il capitale umano cresce di più di tutto — diploma o laurea fra i 25-64enni passa da ",
      virgola(cambio$valore_1991[cambio$indicatore == "I6"], 1), "%\n",
      "a ", virgola(cambio$valore_2011[cambio$indicatore == "I6"], 1),
      "% — ma la Sicilia cresce di più: quello stesso indicatore scende dal ",
      virgola(primi$percentile_fav[primi$indicatore == "I6"], 0), "° al ",
      virgola(ultimi$percentile_fav[ultimi$indicatore == "I6"], 0), "° percentile.\n",
      "L'occupazione giovanile è il caso limite: ",
      paste0("+", virgola(cambio$variazione_valore_pp[cambio$indicatore == "L14"], 1)),
      " punti in vent'anni (",
      virgola(cambio$valore_1991[cambio$indicatore == "L14"], 1), "% → ",
      virgola(cambio$valore_2011[cambio$indicatore == "L14"], 1),
      "%) valgono un crollo dal ", virgola(primi$percentile_fav[primi$indicatore == "L14"], 0),
      "° al ", virgola(ultimi$percentile_fav[ultimi$indicatore == "L14"], 0), "° percentile."), LARGHEZZA),
    caption = didascalia(paste0(
      "Fonte: ISTAT, 8milaCensus - censimenti 1991, 2001, 2011. Fasce diverse per indicatore, indicate nel nome.\n",
      "Percentile favorevole = percentile fra i 390 comuni siciliani, ribaltato (100 − p) su uscita precoce e NEET, dove il valore alto è sfavorevole.\n",
      "Dopo il ribaltamento un percentile alto significa sempre \"davanti agli altri comuni\". Le etichette di fine linea sono scostate quanto basta a non sovrapporsi; i pallini stanno sul valore vero.\n",
      "Migliorare e arretrare non sono in contraddizione: la quota di Bagheria sale, quella della mediana regionale sale di più. La figura misura la seconda cosa, che è quella che una policy di convergenza deve spostare.\n",
      "Il confronto è fermo al 2011: 8milaCensus non prosegue oltre, e le tavole 2018-2024 hanno definizioni diverse. I due periodi non formano una serie continua e non vanno letti come tale.\n",
      "Elaborazione: pipeline/edu (thread educazione) - data/processed/edu_historical_bagheria.csv, edu_historical_change_1991_2011.csv"), LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "edu_fig01_storia_posizione", larghezza = LARGHEZZA, altezza = 16)
