# Figura edu-10 (appendice B) — la mobilità come contesto, e i suoi tre buchi.
# Claim del thread educazione (invariato): il mercato esterno conta, ma l'accessibilità
# non è misurata. Il pendolarismo recente NON identifica Palermo come destinazione; gli
# indicatori storici M2 e M6 hanno denominatori diversi; il GTFS AMAT descrive la rete
# urbana palermitana, non il collegamento Bagheria-Palermo. La mobilità può entrare nel
# pilota solo come barriera registrata e testata su uno specifico sottogruppo.
#
# PERCHÉ QUESTA FORMA E NON DUE BARRE AFFIANCATE (figures/edu/13).
# Il difetto grave stava nel pannello destro: M2 e M6 erano due barre adiacenti dentro la
# stessa cornice, con la stessa scala e la stessa unità apparente, e la caption diceva —
# in piccolo — che hanno denominatori diversi. Sono davvero incommensurabili: M2 è una
# quota della POPOLAZIONE fino a 64 anni, M6 una quota dei soli PENDOLARI. Affiancarle
# invita esattamente al confronto che la nota vieta ("a Bagheria M2 è più alto di M6"),
# e una figura non deve fidarsi di una nota per non essere letta male. Qui vivono in due
# pannelli separati, ciascuno con il proprio asse e il proprio denominatore scritto sopra:
# la lettura sbagliata non è vietata, è resa impossibile dal disegno.
# Il pannello sinistro guadagna invece la seconda metà di un dato che c'era già: la tavola
# del pendolarismo porta il MOTIVO dello spostamento, e la versione precedente ne mostrava
# solo "lavoro". Studio e lavoro come dumbbell mettono la distanza fra i due dove si
# legge — come lunghezza — invece che come differenza fra due grafici.
#
# Colore: studio e lavoro prendono i colori che quegli stati hanno in tutta la cartella
# (COLORI_STATO). Bagheria resta riconoscibile dalla posizione in cima e dall'etichetta
# di riga, non da una tinta: qui le righe sono territori e la tinta serve al motivo.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 29

pendolarismo <- read_csv(file.path(PROCESSED, "edu_census_commuting_long.csv"),
                         show_col_types = FALSE)
storici <- read_csv(file.path(PROCESSED, "edu_commuting_appendix.csv"),
                    show_col_types = FALSE)
dizionario <- read_csv(file.path(PROCESSED, "edu_indicator_dictionary.csv"),
                       show_col_types = FALSE)
gtfs <- read_csv(file.path(PROCESSED, "edu_palermo_gtfs_summary.csv"),
                 show_col_types = FALSE)

CODICI <- c("082006" = "Bagheria", "082053" = "Palermo",
            ITG1 = "Sicilia", IT = "Italia")
ANNO <- max(pendolarismo$anno)

# I due motivi dello spostamento. La tavola li porta entrambi; la versione precedente
# della figura usava solo WK, e la metà mancante è quella che riguarda questo thread.
MOTIVI <- c(WK = "per lavoro", STD = "per studio")
COLORI_MOTIVO <- c(`per lavoro` = COLORI_STATO[["occupati"]],
                   `per studio` = COLORI_STATO[["studenti"]])

# Quota di chi si sposta FUORI COMUNE sul totale di chi si sposta per quel motivo.
# Il denominatore è per motivo, non il totale degli spostamenti: "38% dei pendolari per
# lavoro" e "15% dei pendolari per studio" sono due quote con basi diverse ma coerenti
# fra territori, che è ciò che il confronto richiede.
fuori <- pendolarismo |>
  filter(anno == ANNO, genere == "T", motivo %in% names(MOTIVI),
         destinazione %in% c("ALL", "OMPUR")) |>
  pivot_wider(names_from = destinazione, values_from = valore) |>
  mutate(quota = 100 * OMPUR / ALL,
         territorio_nome = factor(CODICI[territorio], levels = rev(ORDINE)),
         motivo_nome = factor(MOTIVI[motivo], levels = MOTIVI))

stopifnot(nrow(fuori) == length(CODICI) * length(MOTIVI), !any(is.na(fuori$quota)))

# Il pannello sinistro deve riprodurre il numero che la versione precedente mostrava:
# se la ricostruzione dalla tavola long divergesse dalla tavola d'appendice, una delle
# due sarebbe sbagliata e la figura non deve sceglierne una in silenzio.
controllo <- fuori |>
  filter(motivo == "WK") |>
  inner_join(select(storici, territorio, atteso = quota_lavoratori_fuori_comune_sui_pendolari),
             by = "territorio")
stopifnot(nrow(controllo) == length(CODICI), all(abs(controllo$quota - controllo$atteso) < 0.05))

quota_di <- function(terr, m) fuori$quota[fuori$territorio_nome == terr & fuori$motivo == m]

# --- pannello A: quello che si misura -------------------------------------------------
divario <- fuori |>
  summarise(da = min(quota), a = max(quota), .by = territorio_nome)

misurato <- ggplot(fuori, aes(quota, territorio_nome)) +
  geom_segment(data = divario, aes(x = da, xend = a, yend = territorio_nome),
               linewidth = 2.2, colour = "grey85", lineend = "round") +
  geom_point(aes(colour = motivo_nome), size = 4.6) +
  geom_text(aes(label = virgola(quota, 1, "%"), colour = motivo_nome),
            nudge_y = 0.28, vjust = 0, size = 3.1, fontface = "bold",
            show.legend = FALSE) +
  scale_colour_manual(values = COLORI_MOTIVO, name = NULL) +
  guides(colour = guide_legend(override.aes = list(size = 4.6))) +
  scale_x_continuous(limits = c(-2, 56), breaks = seq(0, 50, 10),
                     labels = function(x) virgola(x, 0, "%"),
                     expand = expansion(mult = 0)) +
  # Le etichette stanno sopra i pallini: senza margine in cima, quella della riga più
  # alta finisce oltre il bordo del pannello e viene tagliata.
  scale_y_discrete(expand = expansion(add = c(0.55, 0.85))) +
  coord_cartesian(clip = "off") +
  labs(subtitle = paste0("Quello che si misura: chi esce dal comune, e per cosa\n",
                         "quota sui pendolari di quel motivo, ", ANNO),
       x = "quota dei pendolari di quel motivo", y = NULL)

# --- pannello B: i due indicatori storici, tenuti separati ---------------------------
# Ogni indicatore col SUO denominatore scritto in cima al pannello. È l'unico modo di
# mostrarli insieme senza suggerire che siano confrontabili fra loro.
INDICATORI_M <- tibble::tribble(
  ~indicatore, ~breve,                ~denominatore,                     ~coda_descrizione,
  "M2",        "mobilità fuori comune", "su popolazione fino a 64 anni",  "popolazione residente di età fino a 64 anni",
  "M6",        "uso del mezzo collettivo", "su chi si sposta ogni giorno", "popolazione residente che si sposta giornalmente per motivi di lavoro o di studio")

# I due denominatori NON si dichiarano a memoria: si verificano sulla coda della
# descrizione ufficiale. È l'affermazione su cui poggia l'intero pannello — che i due
# indicatori non siano confrontabili — e se il dizionario la smentisse la figura,
# disegnandoli comunque separati, direbbe una cosa che il dato non sostiene più.
nomi_m <- INDICATORI_M |>
  inner_join(select(dizionario, indicatore, descrizione), by = "indicatore") |>
  mutate(titolo = paste0(indicatore, " · ", breve, "\n", denominatore))
stopifnot(nrow(nomi_m) == nrow(INDICATORI_M),
          mapply(endsWith, nomi_m$descrizione, nomi_m$coda_descrizione),
          n_distinct(nomi_m$coda_descrizione) == nrow(nomi_m))

mobilita_storica <- storici |>
  select(territorio, all_of(INDICATORI_M$indicatore)) |>
  pivot_longer(-territorio, names_to = "indicatore", values_to = "valore") |>
  inner_join(select(nomi_m, indicatore, titolo), by = "indicatore") |>
  mutate(territorio_nome = factor(CODICI[territorio], levels = rev(ORDINE)),
         pannello = factor(titolo, levels = nomi_m$titolo))

stopifnot(nrow(mobilita_storica) == length(CODICI) * nrow(INDICATORI_M))

storica <- ggplot(mobilita_storica, aes(valore, territorio_nome)) +
  # Pannelli separati e scala libera: due indicatori con denominatori diversi non
  # condividono un asse, altrimenti la vicinanza suggerisce una comparabilità che non c'è.
  facet_wrap(~pannello, ncol = 1, scales = "free_x") +
  theme(panel.spacing.y = unit(1.4, "lines")) +
  geom_segment(aes(x = 0, xend = valore, yend = territorio_nome), linewidth = 2.2,
               colour = "grey85", lineend = "round") +
  geom_point(size = 4.2, colour = "grey35") +
  geom_text(aes(label = virgola(valore, 1, "%")), hjust = 0, nudge_x = 0.55,
            size = 3.1, fontface = "bold", colour = "grey20") +
  scale_x_continuous(labels = function(x) virgola(x, 0, "%"),
                     expand = expansion(mult = c(0, 0.26))) +
  scale_y_discrete(expand = expansion(add = c(0.6, 0.6))) +
  labs(subtitle = paste0("Gli storici, un pannello per denominatore\n",
                         "censimento 2011 (mai da confrontare fra loro)"),
       x = NULL, y = NULL)

figura <- (misurato | storica) +
  plot_layout(widths = c(1.1, 1)) +
  plot_annotation(
    title = "Da Bagheria si esce per lavorare molto più che per studiare, e dove si vada resta fuori dal dato",
    subtitle = sommario(paste0(
      "Appendice sulla mobilità: nel pannello di sinistra la quota di chi esce dal comune sul totale di chi si sposta ogni giorno per quel motivo, per quattro territori e per i due motivi (lavoro e studio), anno ",
      ANNO, "; nei pannelli di destra due indicatori storici di mobilità del censimento 2011, ciascuno con il proprio denominatore. La figura descrive e non spiega: serve a dire cosa la mobilità permette di affermare e cosa no.\n",
      "Nel ", ANNO, " il ", virgola(quota_di("Bagheria", "WK"), 1),
      "% di chi si sposta per lavoro esce dal comune, contro il ",
      virgola(quota_di("Bagheria", "STD"), 1), "% di chi si sposta per studio: ",
      virgola(quota_di("Bagheria", "WK") - quota_di("Bagheria", "STD"), 1),
      " punti di distanza, la più larga dopo quella italiana.\n",
      "Rispetto alla Sicilia Bagheria manda fuori PIÙ lavoratori (",
      virgola(quota_di("Bagheria", "WK"), 1), "% contro ", virgola(quota_di("Sicilia", "WK"), 1),
      "%) e MENO studenti (", virgola(quota_di("Bagheria", "STD"), 1), "% contro ",
      virgola(quota_di("Sicilia", "STD"), 1), "%). È una descrizione, non una spiegazione.\n",
      "Quello che manca è ciò che servirebbe a farne una policy: la tavola si ferma a «fuori comune», quindi la destinazione resta ignota;\n",
      "i due indicatori storici hanno denominatori incompatibili e stanno in due pannelli separati; e il GTFS disponibile copre la rete urbana di Palermo, non il collegamento da Bagheria."),
      LARGHEZZA),
    caption = didascalia_2b(
      lettura = paste0(
        "nel pannello di sinistra ogni riga è un territorio e i due pallini sono i due motivi dello spostamento: la loro distanza descrive quel territorio, non un divario fra lavoro e studio, perché i pendolari per lavoro e quelli per studio sono due popolazioni distinte. ",
        "Il confronto legittimo è quindi fra territori sullo stesso motivo. ",
        "Nei pannelli di destra ogni pannello ha il suo asse perché i due indicatori non condividono il denominatore (M2 rapporta chi esce dal comune alla popolazione fino a 64 anni, M6 rapporta chi usa il mezzo collettivo ai soli residenti che si spostano ogni giorno): le due altezze non vanno confrontate a occhio. ",
        "Bagheria è in vermiglio, gli altri territori restano in grigio o nei colori che portano in tutta la cartella. ",
        "Palermo compare a valori bassissimi per costruzione e non per merito: è il capoluogo del proprio bacino, quindi i suoi residenti trovano lavoro e scuole dentro il comune. ",
        "La destinazione non è nel dato: la tavola distingue solo «stesso comune» e «altro comune», e nessun numero di questa figura dice quante persone vanno a Palermo. ",
        "Il feed GTFS disponibile (", gtfs$feed_publisher, ", ", gtfs$feed_version, ": ", migliaia(gtfs$routes),
        " linee, ", migliaia(gtfs$stops), " fermate) descrive la rete urbana di Palermo e non include il tratto Bagheria-Palermo, quindi nessun risultato ne dipende. ",
        "La mobilità resta contesto: nel pilota può entrare solo come barriera registrata caso per caso e testata su uno specifico sottogruppo, mai come causa identificata del divario occupazionale."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola del pendolarismo giornaliero, ", ANNO,
        " (pannello sinistro), e ISTAT, 8milaCensus, censimento 2011 (pannelli destri). ",
        "Elaborazione: pipeline/edu (thread educazione), data/processed/edu_census_commuting_long.csv, edu_commuting_appendix.csv, edu_indicator_dictionary.csv e edu_palermo_gtfs_summary.csv."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "edu_fig10_appendice_mobilita", larghezza = LARGHEZZA, altezza = 26)
