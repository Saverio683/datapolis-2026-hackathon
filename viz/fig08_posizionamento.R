# Figura 8 — la terza lente di confronto: il gruppo dei pari strutturali.
# Le altre figure confrontano Bagheria con la gerarchia amministrativa (Palermo, Sicilia,
# Italia) e con il vicinato geografico. Qui il confronto è con i dieci comuni siciliani
# più simili per struttura — dimensione, densità, età, stranieri, abitazioni, distanza da
# Palermo — appaiati nel notebook su variabili che non sono esiti.
# Serve a separare due cose che una policy comunale tratta in modo opposto: lo svantaggio
# che Bagheria condivide con chi le somiglia (e su cui un intervento locale può poco) da
# quello su cui è un caso a sé.
# `verso` (quale direzione è "meglio") arriva dal notebook: è una scelta interpretativa e
# non va rifatta qui. Il colore la usa, la posizione mostra il dato grezzo.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

posizionamento <- read_csv(file.path(PROCESSED, "genere_posizionamento.csv"),
                           show_col_types = FALSE)

# Nomi corti per l'asse: quelli per esteso stanno nella colonna `nome` del CSV.
BREVI <- c(L11 = "occupazione femminile 15+",
           L7  = "disoccupazione femminile 15+",
           I1  = "differenziale educativo M/F",
           L4  = "NEET 15-29",
           F4  = "giovani che vivono da soli",
           F7  = "coppie giovani con figli",
           M2  = "mobilità fuori comune")

N_GEMELLE <- posizionamento$n_gemelle[1]
N_REGIONE <- posizionamento$n_regione[1]
MEDIANA_GEMELLE <- N_GEMELLE / 2

#' Colore di una riga: si tinge solo quando Bagheria esce dalla metà centrale del
#' riferimento, altrimenti resta grigia. Serve a non trasformare uno scarto di una
#' posizione (3/10 contro 5/10) in un'affermazione categorica: il notebook quei casi
#' li chiama "nella norma", e la figura deve dire la stessa cosa.
#' `verso` arriva dal notebook; qui si moltiplicano due segni già stabiliti altrove.
giudica <- function(verso, dentro_la_norma, sopra) {
  case_when(verso == 0 | dentro_la_norma ~ "neutro",
            verso * ifelse(sopra, 1, -1) < 0 ~ "peggio",
            TRUE ~ "meglio")
}

dati <- posizionamento |>
  mutate(
    breve = ifelse(verso == 0, paste0(BREVI[indicatore], " *"), BREVI[indicatore]),
    # Nel gruppo: "estrema" = fuori dall'intervallo interquartile delle gemelle.
    giudizio_gemelle = giudica(verso,
                               bagheria >= gemelle_q1 & bagheria <= gemelle_q3,
                               bagheria > gemelle_q3),
    # Nella regione: stessa idea, sui quartili della distribuzione dei 390.
    giudizio_regione = giudica(verso,
                               percentile_390 >= 25 & percentile_390 <= 75,
                               percentile_390 > 50),
    breve = factor(breve, levels = rev(breve[order(gemelle_sotto)])))

# La legenda dice cosa significano i tre colori: prima stava nel sottotitolo, che è il
# posto sbagliato per una chiave di lettura — si legge una volta e poi non si ritrova più
# mentre si guarda il grafico. `limits` fissa le tre voci anche se una classe non comparisse
# nel dato, così la chiave è sempre completa.
ETICHETTE_GIUDIZIO <- c(peggio = "Bagheria sta peggio del riferimento",
                        neutro = "nella norma, o indicatore senza verso \"buono\" (*)",
                        meglio = "Bagheria sta meglio del riferimento")
scala_giudizio <- function() {
  list(scale_colour_manual(values = DIVERGENTE, limits = names(DIVERGENTE),
                           labels = ETICHETTE_GIUDIZIO, name = NULL),
       guides(colour = guide_legend(override.aes = list(size = 4.6))))
}

# --- pannello A: la posizione dentro il gruppo delle gemelle ------------------------
gruppo <- ggplot(dati, aes(gemelle_sotto, breve, colour = giudizio_gemelle)) +
  geom_vline(xintercept = MEDIANA_GEMELLE, colour = "grey80", linewidth = 0.4) +
  geom_segment(aes(x = MEDIANA_GEMELLE, xend = gemelle_sotto, yend = breve),
               linewidth = 2.4, lineend = "round") +
  geom_point(size = 4.6) +
  geom_text(aes(label = paste0(gemelle_sotto, "/", N_GEMELLE)),
            nudge_x = ifelse(dati$gemelle_sotto >= MEDIANA_GEMELLE, 0.7, -0.7),
            size = 3.3, fontface = "bold", colour = "grey20") +
  scala_giudizio() +
  scale_x_continuous(limits = c(-1.1, N_GEMELLE + 1.1), breaks = seq(0, N_GEMELLE, 2),
                     expand = expansion(mult = 0)) +
  labs(subtitle = paste0("Dentro il gruppo dei pari strutturali\n",
                         "quante delle ", N_GEMELLE, " gemelle stanno sotto Bagheria"),
       x = paste0("comuni sotto Bagheria (", MEDIANA_GEMELLE, " = mediana del gruppo)"),
       y = NULL)

# --- pannello B: la posizione nella regione ------------------------------------------
regione <- ggplot(dati, aes(percentile_390, breve, colour = giudizio_regione)) +
  geom_vline(xintercept = 50, colour = "grey80", linewidth = 0.4) +
  geom_segment(aes(x = 50, xend = percentile_390, yend = breve),
               linewidth = 2.4, lineend = "round") +
  geom_point(size = 4.6) +
  geom_text(aes(label = virgola(percentile_390, 0, "°")),
            nudge_x = ifelse(dati$percentile_390 >= 50, 7, -7),
            size = 3.3, fontface = "bold", colour = "grey20") +
  scale_colour_manual(values = DIVERGENTE, guide = "none") +
  scale_x_continuous(limits = c(-11, 111), breaks = seq(0, 100, 25),
                     expand = expansion(mult = 0)) +
  labs(subtitle = paste0("E dentro la regione\n",
                         "percentile sui ", N_REGIONE, " comuni siciliani"),
       x = "percentile (50 = mediana regionale)", y = NULL) +
  theme(axis.text.y = element_blank())

figura <- (gruppo | regione) +
  plot_layout(widths = c(1, 1), guides = "collect") +
  plot_annotation(
    title = "Lo svantaggio giovanile è di fascia territoriale; il tratto di Bagheria è l'autonomia dei suoi giovani",
    subtitle = paste0(
      "Il confronto con Palermo, la Sicilia e l'Italia dice quanto Bagheria è indietro; quello con i comuni che le somigliano dice di chi è il problema.\n",
      "Sul NEET Bagheria è dentro i quartili del suo gruppo — grigio a sinistra — ma all'87° percentile regionale: rosso a destra.\n",
      "È il ritratto di uno svantaggio di fascia, che una policy comunale da sola non sposta. Vale anche per l'occupazione femminile.\n",
      "Il tratto suo è altrove, e le due letture concordano: nessuna gemella ha meno giovani che vivono da soli (3° percentile\n",
      "regionale), una sola ha un vantaggio educativo femminile più marcato, solo due hanno meno mobilità."),
    caption = paste0(
      "Fonte: ISTAT, 8milaCensus, censimento 2011.\n",
      "Fasce diverse per indicatore: 15+ (occupazione e disoccupazione F), 6+ (differenziale educativo), 15-29 (NEET), totale famiglie (giovani soli, coppie con figli), residenti (mobilità).\n",
      "Gemelle = i ", N_GEMELLE, " comuni più simili a Bagheria per dimensione, densità, età, stranieri, abitazioni e distanza da Palermo\n",
      "(matching Mahalanobis su variabili non-esito; robustezza 8/", N_GEMELLE, " e 6/", N_GEMELLE, " sugli altri metodi).\n",
      "Il verso è fissato nel notebook: alto è meglio per occupazione femminile e giovani soli, peggio per disoccupazione, NEET e differenziale educativo M/F. (*) F7 e M2 restano descrittivi.\n",
      "Il colore compare solo fuori dalla metà centrale del riferimento: oltre i quartili delle gemelle a sinistra, sotto il 25° o sopra il 75° percentile regionale a destra.\n",
      "Il pallino mostra sempre la posizione, anche quando è grigio.\n",
      "Anno e fascia diversi dalle serie 15-24 del thread: è il gruppo di controllo storico, mai un termine di paragone con il censimento permanente 2018-2024.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_posizionamento.csv"),
    theme = tema_figura()
  )

salva(figura, "fig08_posizionamento", larghezza = 28, altezza = 17.5)
