# Figura 4 — la Sicilia del 2024, e quanto somiglia a quella del 2011.
# I poligoni arrivano già proiettati da pipeline/build.py (ISTAT 2026 generalizzati,
# EPSG:32633 — WGS 84 / UTM 33N): qui non si tocca la geometria, si disegna.
# Niente sf: le librerie di sistema GDAL/GEOS non sono installabili su questa macchina.
# Il punto per la proposal: Bagheria arriva nel 2024 dove la Sicilia stava nel 2011 —
# il livello sale, la posizione no. Che la graduatoria del 2011 predica quella del 2024,
# cioè che un claim costruito sul censimento vecchio fosse una previsione e non una
# scommessa sul passato, è un'affermazione metodologica e sta in fig04b.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 26   # stessa misura del salvataggio: su questa il testo va a capo

confini <- read_csv(file.path(PROCESSED, "genere_mappa_occupazione_femminile.csv"),
                    col_types = cols(territorio = "c", nome_comune = "c", .default = "d"))
# Un valore per comune alle due estremità della serie: la geometria sta nel file dei
# vertici, i valori qui. Il join è assemblaggio, non trasformazione — nessun ricalcolo.
comuni <- read_csv(file.path(PROCESSED, "genere_mappa_2011_2024.csv"),
                   col_types = cols(territorio = "c", nome_comune = "c", ruolo = "c",
                                    .default = "d"))
distribuzione <- read_csv(file.path(PROCESSED, "genere_distribuzione_390.csv"),
                          col_types = cols(fonte = "c", .default = "d"))

ANNO <- max(distribuzione$anno)
BASE <- min(distribuzione$anno)
riga <- function(anno) distribuzione[distribuzione$anno == anno, ]
prima <- riga(BASE)
dopo <- riga(ANNO)

mappa <- left_join(confini, select(comuni, territorio, occ_2024), by = "territorio")
bagheria <- filter(comuni, ruolo == "Bagheria")
vicini <- filter(comuni, ruolo == "vicino") |> arrange(distanza_km)

palermo <- filter(comuni, territorio == "082053")
stopifnot(nrow(palermo) == 1)

# Bagheria e i cinque vicini stanno dentro 8 km: sulla carta dell'isola, larga 335 km,
# sono un'unghia. Le etichette si impilano quindi in mare, con nome e valore in una stringa
# sola (con due colonne allineate il nome più lungo tocca il valore, e il blocco non ha
# spazio per allargarsi: deve stare fra Ustica, x 341000, e Alicudi, x 442000).
#
# Una linea di richiamo per comune, com'era prima, si intrecciava con le altre senza
# distinguere niente: a quella distanza nessuno può appaiare la propria linea al proprio
# poligono, e sei rette verso lo stesso punto sono sei volte lo stesso richiamo. Al loro
# posto una graffa — verticale lungo il blocco, poi una sola discesa al gruppo — che dice
# la cosa vera: queste sei righe stanno tutte lì.
# Palermo no: 17,5 km più a ovest, poligono grande e riconoscibile, e non è un vicino ma il
# termine di paragone. Riga staccata dal blocco, richiamo suo, viola come in ogni altra
# figura della cartella.
# Le coordinate del blocco cadono su tratti di Tirreno senza comuni (verificato sui vertici).
# Gli estremi regionali non sono etichettati sulla carta: cambiano comune fra le due annate
# e si leggono meglio agli estremi dell'istogramma qui sotto.
X_NOME <- 370000
X_GRAFFA <- X_NOME - 2500
PASSO <- 9500

# Blocco in ordine decrescente di occupazione femminile: la colonna si legge come una
# classifica, e dove cade Bagheria dentro il suo stesso vicinato — quarta su sei — è parte
# di quello che la figura dice. L'ordine per distanza che c'era prima rispondeva a una
# domanda che nessuno stava facendo.
# Palermo apre il blocco perché ha il valore più alto, ma resta staccata di mezzo passo in
# più: la graffa non la prende, e il suo richiamo va per conto suo.
riga_palermo <- palermo |>
  mutate(y_lab = 4290000, colore = COLORI_TERRITORIO[["Palermo"]], faccia = "bold")
gruppo <- bind_rows(bagheria, vicini) |>
  arrange(desc(occ_2024)) |>
  mutate(y_lab = riga_palermo$y_lab - PASSO * 1.6 - PASSO * (row_number() - 1),
         colore = if_else(ruolo == "Bagheria", COLORI_TERRITORIO[["Bagheria"]], "grey20"),
         faccia = if_else(ruolo == "Bagheria", "bold", "plain"))
pila <- bind_rows(riga_palermo, gruppo) |>
  mutate(testo = paste0(nome_comune, "  ", virgola(occ_2024, 1, "%")))
# Il blocco deve leggersi come una classifica: se un giorno Palermo non fosse più in testa,
# la riga staccata in cima diventerebbe una bugia tipografica.
stopifnot(!is.unsorted(rev(pila$occ_2024)))
# Il richiamo di Palermo parte sotto la graffa e va a sinistra, il suo poligono sta lì:
# se un giorno finisse sopra, le due linee si incrocerebbero e la graffa non terrebbe.
stopifnot(riga_palermo$y_lab > palermo$y, palermo$x < X_GRAFFA)
# Le due frasi del sottotitolo sul vicinato e su Palermo: se il verso cambiasse andrebbero
# riscritte, non ristampate.
stopifnot(all(vicini$occ_2024 < dopo$mediana), palermo$occ_2024 > dopo$mediana)

# La centralità della carta è quella dell'isola, non dell'inquadratura. Pantelleria, le
# Egadi, Ustica, le Eolie e Lampedusa stanno fino a 110 km al largo: se entrano nel conto
# del riquadro ne spostano il centro a ovest (391500 contro i 415238 della terraferma), e
# la Sicilia scivola a destra lasciando il vuoto in basso a sinistra. Il centro lo dà
# quindi la sola terraferma; la larghezza resta quella di prima, così la carta non
# rimpicciolisce — si sposta e basta. Fuori riquadro finiscono Pantelleria e Marettimo,
# che restano nel dato e nella distribuzione qui sotto, come Lampedusa e Linosa.
ISOLE_MINORI <- c("Pantelleria", "Favignana", "Ustica", "Lipari", "Malfa",
                  "Santa Marina Salina", "Leni", "Lampedusa e Linosa")
stopifnot(all(ISOLE_MINORI %in% confini$nome_comune))
LARGHEZZA_RIQUADRO <- 335000
XLIM <- mean(range(confini$x[!confini$nome_comune %in% ISOLE_MINORI])) +
  c(-1, 1) * LARGHEZZA_RIQUADRO / 2
YLIM <- c(4050000, 4300000)

#' Il riquadro non deve tagliare a metà nessun poligono: una parte o è dentro o è fuori,
#' altrimenti la carta mostra mezza isola e non lo dice da nessuna parte. È il motivo per
#' cui `coord_equal` qui va con `expand = FALSE`: il 5% di margine che aggiunge di default
#' vale 16,7 km, più della distanza fra Pantelleria e il bordo, e la rimetteva dentro
#' per metà — con un lato dritto, che su una carta si legge come una costa.
dentro <- function(x, y) x >= XLIM[1] & x <= XLIM[2] & y >= YLIM[1] & y <= YLIM[2]
stopifnot(!any(summarise(confini, taglia = any(dentro(x, y)) & !all(dentro(x, y)),
                         .by = c(nome_comune, parte))$taglia))

# group = comune × parte (le isole sono parti separate), subgroup = anello (i buchi).
forma <- aes(x, y, group = interaction(territorio, parte), subgroup = anello)
SCALA <- c(12, 40)   # comune a carta e istogramma: i due pannelli si leggono insieme

carta <- ggplot() +
  geom_polygon(data = mappa, modifyList(forma, aes(fill = occ_2024)),
               rule = "evenodd", colour = "white", linewidth = 0.08) +
  geom_polygon(data = filter(mappa, territorio %in% vicini$territorio),
               forma, rule = "evenodd", fill = NA, colour = "grey15", linewidth = 0.3) +
  geom_polygon(data = filter(mappa, territorio == palermo$territorio), forma,
               rule = "evenodd", fill = NA, colour = COLORI_TERRITORIO[["Palermo"]],
               linewidth = 0.7) +
  # Bagheria per ultima e sopra tutti: confina con Santa Flavia e Ficarazzi, e disegnata
  # prima si farebbe coprire il bordo. Colore che stacca dalla scala viridis.
  geom_polygon(data = filter(mappa, territorio == bagheria$territorio), forma,
               rule = "evenodd", fill = NA, colour = "#D55E00", linewidth = 0.9) +
  # La graffa: il montante lungo il blocco, poi una discesa sola fino al grappolo.
  annotate("segment", x = X_GRAFFA, xend = X_GRAFFA,
           y = max(gruppo$y_lab), yend = min(gruppo$y_lab),
           colour = "grey45", linewidth = 0.3) +
  annotate("segment", x = X_GRAFFA, xend = bagheria$x,
           y = min(gruppo$y_lab), yend = bagheria$y,
           colour = "grey45", linewidth = 0.3) +
  annotate("segment", x = X_GRAFFA, xend = palermo$x,
           y = riga_palermo$y_lab, yend = palermo$y,
           colour = COLORI_TERRITORIO[["Palermo"]], linewidth = 0.3) +
  geom_text(data = pila, aes(X_NOME, y_lab, label = testo, colour = colore,
                             fontface = faccia), hjust = 0, size = 3.2) +
  scale_colour_identity() +
  scale_fill_viridis_c(name = paste0("occupazione femminile ", ANNO, " (%)"),
                       limits = SCALA, na.value = "grey88", breaks = seq(15, 40, 5),
                       guide = guide_colourbar(barwidth = 9, barheight = 0.45,
                                               title.position = "top")) +
  # Riquadro sull'isola: Lampedusa e Linosa (250 km più a sud) lascerebbero mezza tela
  # vuota. Il comune resta nella distribuzione qui sotto e nel dato, solo fuori inquadratura.
  # Il clip resta acceso, altrimenti Lampedusa viene disegnata fuori dal pannello, sopra
  # l'istogramma; le etichette stanno tutte dentro il riquadro.
  # `XLIM` è centrato sulla terraferma (sopra); `YLIM` no, e non per distrazione: la fascia
  # di mare a nord non è vuota — ci stanno la legenda, il blocco delle etichette, Ustica e
  # le Eolie. Centrarla sulla terraferma la taglierebbe via.
  # expand = FALSE: il riquadro disegnato dev'essere quello su cui è fatto il conto del
  # centro e quello che il controllo qui sopra verifica, non quello più il 5%.
  coord_equal(xlim = XLIM, ylim = YLIM, expand = FALSE) +
  labs(x = NULL, y = NULL) +
  # panel.grid da solo non basta: tema_datapolis fissa esplicitamente major e minor,
  # e un figlio impostato vince sul genitore azzerato.
  # La barra di colore torna dentro il pannello, in alto a sinistra: è l'unica figura
  # della cartella dove sta dentro il disegno, e la ragione è che qui il pannello ha una
  # forma imposta. `coord_equal` lega altezza e larghezza al rapporto della Sicilia
  # (335 km per 250), quindi ogni centimetro speso in una fascia sopra la carta è un
  # centimetro che la carta non usa in larghezza: la fascia costava il 15% del disegno.
  # L'obiezione di prima resta vera — dentro il pannello la chiave si trova solo
  # cercandola — ed è pagata mettendola nell'angolo che si legge per primo, sul Tirreno a
  # nord-ovest, dove non c'è terraferma e non arriva il blocco delle etichette (x 370000,
  # cioè al 44% della larghezza).
  theme(axis.text = element_blank(), axis.ticks = element_blank(),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        legend.position = "inside", legend.position.inside = c(0, 1),
        legend.justification.inside = c(0, 1), legend.direction = "horizontal",
        legend.margin = margin(0, 0, 0, 0),
        legend.title = element_text(size = rel(0.85), hjust = 0))

# --- pannello B: la distribuzione si è spostata, Bagheria si è spostata con lei --------
# Barre piene = 2024 (stessa scala colore della carta), profilo grigio = 2011. Sovrapposti
# e non affiancati perché il finding è lo scorrimento dell'intera distribuzione.
spostamento <- ggplot(comuni, aes(occ_2024)) +
  geom_histogram(aes(fill = after_stat(x)), binwidth = 1, colour = "white", linewidth = 0.15) +
  geom_histogram(aes(x = occ_2011), binwidth = 1, fill = NA, colour = "grey35",
                 linewidth = 0.4) +
  annotate("segment", x = prima$bagheria, xend = dopo$bagheria, y = 43, yend = 43,
           colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 0.5,
           arrow = arrow(length = unit(0.18, "cm"), type = "closed")) +
  annotate("segment", x = c(prima$bagheria, dopo$bagheria),
           xend = c(prima$bagheria, dopo$bagheria), y = 0, yend = 43,
           colour = COLORI_TERRITORIO[["Bagheria"]], linetype = c("dashed", "solid"),
           linewidth = c(0.4, 0.8)) +
  annotate("text", x = prima$bagheria - 0.7, y = 43, hjust = 1, vjust = 0.4, size = 3.1,
           colour = COLORI_TERRITORIO[["Bagheria"]], lineheight = 1.05,
           label = paste0("Bagheria ", BASE, "\n", virgola(prima$bagheria, 1, "%"))) +
  annotate("text", x = dopo$bagheria + 0.7, y = 43, hjust = 0, vjust = 0.4, size = 3.1,
           fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]], lineheight = 1.05,
           label = paste0("Bagheria ", ANNO, "\n", virgola(dopo$bagheria, 1, "%"))) +
  # Le due mediane: la distanza fra loro è lo scorrimento che Bagheria ha solo inseguito.
  annotate("segment", x = c(prima$mediana, dopo$mediana),
           xend = c(prima$mediana, dopo$mediana), y = 0, yend = 34,
           colour = "grey35", linetype = c("dashed", "solid"), linewidth = c(0.4, 0.7)) +
  annotate("text", x = dopo$mediana + 0.6, y = 40, hjust = 0, vjust = 1, size = 3,
           colour = "grey30", lineheight = 1.05,
           label = paste0("mediana siciliana\n", BASE, ": ", virgola(prima$mediana, 1, "%"),
                          "   ", ANNO, ": ", virgola(dopo$mediana, 1, "%"))) +
  scale_fill_viridis_c(limits = SCALA, guide = "none") +
  # xlim su coord e non su scale: la scala scarterebbe i comuni fuori intervallo prima
  # del binning (e infatti avvisava), il coord si limita a ritagliare la vista.
  scale_x_continuous(labels = function(x) paste0(x, "%")) +
  coord_cartesian(xlim = SCALA, clip = "off") +
  labs(subtitle = paste0("Tutta la Sicilia si è spostata a destra, Bagheria l'ha seguita\n",
                         "barre piene ", ANNO, ", profilo grigio ", BASE,
                         "; 390 comuni, 15 anni e più"),
       x = "tasso di occupazione femminile", y = "comuni") +
  theme(panel.grid.major.x = element_blank())

# La prova che questa fotografia non è scaduta — la graduatoria del 2011 predice quella
# del 2024 — sta in fig04b: è un'affermazione metodologica, non geografica, e in un
# terzo di riga sotto la carta stava stretta, con le annotazioni sopra la nuvola.
figura <- carta / spostamento +
  # 7,2 contro 1,9: con la carta vincolata da `coord_equal` il rapporto non è una
  # preferenza di impaginazione ma il conto che le fa riempire la larghezza — sotto,
  # l'altezza è il lato corto e la Sicilia si stringe lasciando bianco a destra e a
  # sinistra. Se cambia `coord_equal` o il riquadro, va rifatto il conto.
  plot_layout(heights = c(7.2, 1.9)) +
  plot_annotation(
    title = paste0("Nel ", ANNO, " Bagheria arriva dove stava la mediana siciliana nel ", BASE),
    subtitle = sommario(paste0(
      "Tasso di occupazione femminile sulla popolazione di 15 anni e più, per comune siciliano, anno ", ANNO,
      ": in alto la carta dell'isola, in basso la distribuzione dello stesso indicatore confrontata con quella del ", BASE,
      ". Il finding è la differenza fra livello e posizione, e la graduatoria con i nomi sta in fig04c.\n",
      "Il livello di Bagheria sale da ", virgola(prima$bagheria, 1, "%"), " a ",
      virgola(dopo$bagheria, 1, "%"), ", ma la mediana regionale sale da ",
      virgola(prima$mediana, 1, "%"), " a ", virgola(dopo$mediana, 1, "%"), ".\n",
      "La posizione tiene: dal ", virgola(prima$percentile, 0, "°"), " al ",
      virgola(dopo$percentile, 0, "°"), " percentile, con ", dopo$comuni_sotto,
      " comuni su 390 più in basso.\n",
      "Resta nella coda bassa della Sicilia, dov'era già nel ", BASE,
      ". Anche i cinque vicini restano sotto la mediana;\n",
      "Palermo, a ", virgola(palermo$distanza_km, 0), " km, la supera appena (",
      virgola(palermo$occ_2024, 1, "%"), ").\n",
      "Ed è una fotografia ancora valida: la graduatoria del ", BASE, " predice quella del ", ANNO,
      " (rho di Spearman ", virgola(prima$rho_vs_2024, 3), ", in fig04b)."), LARGHEZZA),
    caption = didascalia_2b(
      lettura = paste0(
        "sulla carta il colore è il valore, su scala continua viridis: più chiaro significa occupazione femminile più alta, e la stessa scala vale per le barre dell'istogramma sotto. ",
        "Sono etichettati Bagheria (bordo vermiglio) e i cinque comuni più vicini per distanza fra i centroidi (bordo scuro, tutti entro 8 km): a questa scala i loro poligoni sono un punto, quindi le sei righe sono raccolte da una graffa sola in mare, ordinate per valore decrescente. ",
        "Palermo ha bordo viola e un richiamo suo perché non è un vicino ma il termine di paragone. Gli estremi regionali non sono etichettati sulla carta, perché cambiano comune fra le due annate, e si leggono agli estremi dell'istogramma. ",
        "Misiliscemi, istituito nel 2021 per distacco da Trapani, è disegnato in grigio e resta fuori dai 390 comuni delle due annate: nel ", BASE,
        " non esisteva e il dato non gli è attribuibile. È l'unica esclusione. ",
        "Nell'istogramma le barre piene sono il ", ANNO, " e il profilo grigio vuoto è il ", BASE,
        ": sono sovrapposti e non affiancati perché il finding è lo scorrimento dell'intera distribuzione. ",
        "Le linee verticali tratteggiate sono i valori del ", BASE, " e quelle piene i valori del ", ANNO,
        ", in vermiglio per Bagheria e in grigio per la mediana regionale; la freccia vermiglia misura quanto Bagheria si è spostata. ",
        "Le due annate vengono da due rilevazioni con disegni diversi (universale a questionario il censimento ", BASE,
        ", campionaria sui registri il permanente): il livello ne risente, il rango dentro l'anno molto meno, ed è la ragione per cui il confronto fra annate, in fig04b, usa percentili e non punti percentuali. ",
        "La fascia (15 anni e più) e gli anni sono diversi dalle serie 15-24 del thread: la figura è contesto di lungo periodo, non un termine di paragone. ",
        "Il riquadro della carta è centrato sulla terraferma e non sull'estensione con tutte le isole minori: restano fuori Lampedusa e Linosa, Pantelleria e Marettimo, che sono comunque nel dato e nell'istogramma, mentre Ustica, Levanzo, Favignana e le Eolie sono in carta."),
      fonte = paste0(
        "ISTAT, 8milaCensus, indicatore L11 (censimento ", BASE, ") e Censimento permanente della popolazione (2018-", ANNO,
        ", il 2020 manca alla fonte), tasso di occupazione femminile sulla popolazione di 15 anni e più. ",
        "Confini: ISTAT, unità amministrative generalizzate al 01/01/2026, sistema di riferimento EPSG:32633 (WGS 84 / UTM 33N). ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_mappa_occupazione_femminile.csv, genere_mappa_2011_2024.csv e genere_distribuzione_390.csv)."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

# Più alta dell'originale: coord_equal vincola la carta dall'altezza, quindi l'altezza
# del pannello è ciò che decide quanto la Sicilia riempie i 26 cm di larghezza.
salva(figura, "fig04_mappa_sicilia", larghezza = LARGHEZZA, altezza = 39)
