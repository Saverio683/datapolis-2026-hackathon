# Figura edu-03 — i quattro stati dei 15-24enni, 2018-2024.
# Claim del thread educazione (invariato): la composizione migliora, ma l'inattività non
# studentesca resta intorno al 19%; il 26,9% fuori da lavoro e studio non è una quinta
# categoria, è la somma di chi cerca (7,9%) e di chi non cerca (19,0%).
#
# PERCHÉ QUESTA FORMA E NON LE BARRE IMPILATE (figures/edu/04).
# Nelle barre impilate la banda che porta il claim — gli inattivi non studenti — stava in
# CIMA alla pila, appoggiata su una base che si muove ogni anno. Una banda che galleggia
# non si confronta: per vedere se il 19,6% del 2018 e il 19,0% del 2024 sono lo stesso
# spessore bisogna misurare due segmenti che partono da quote diverse, e a occhio non si
# fa. È il difetto classico della pila: solo il segmento appoggiato allo zero è leggibile.
# Qui l'ordine è ribaltato e gli inattivi stanno SULLA BASE: il loro spessore si legge
# sull'asse, e la banda piatta diventa visibile come piatta. Sopra di loro sta chi cerca,
# così il confine fra le due è l'aggregato "fuori da lavoro e studio" — che il claim
# definisce proprio come la loro somma, e che qui è una linea da seguire invece di due
# numeri da sommare a mente.
# Area e non barre perché l'asse x è tempo: le barre suggeriscono categorie indipendenti,
# l'area dice che fra un'annata e l'altra c'è continuità.
#
# Il 2020 manca alla fonte (tavola lavoro non pubblicata) e non si interpola: l'asse si
# comprime con asse_2020() e la striscia di buco_2020() riempie la colonna vuota.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 26

stati <- read_csv(file.path(PROCESSED, "edu_youth_states_2018_2024.csv"),
                  show_col_types = FALSE) |>
  filter(territorio_nome == "Bagheria")

# L'ordine della pila, dal basso verso l'alto: gli inattivi sullo zero perché sono il
# claim, poi chi cerca — le due componenti di "fuori da lavoro e studio" — e sopra chi
# studia o lavora. `position_stack` impila il primo livello in cima, quindi la lista è
# scritta nell'ordine in cui la si legge dall'alto.
STATI <- tibble::tribble(
  ~colonna,                       ~nome,                     ~colore,
  "quota_studenti",               "studenti",                COLORI_STATO[["studenti"]],
  "quota_occupati",               "occupati",                COLORI_STATO[["occupati"]],
  "quota_in_cerca",               "in cerca di lavoro",      COLORI_STATO[["in cerca"]],
  "quota_inattivi_non_studenti",  "inattivi non studenti",   COLORI_STATO[["casalinghe/i"]])

# I denominatori della fascia: la composizione somma sempre a 100, quindi senza i conteggi
# non si sa se la banda che si assottiglia valga trenta persone o trecento.
enne_anno <- function(a) stati$popolazione[stati$territorio_nome == "Bagheria" & stati$anno == a]
ANNI_STATI <- range(stati$anno[stati$territorio_nome == "Bagheria"])

serie <- stati |>
  select(anno, all_of(STATI$colonna)) |>
  pivot_longer(-anno, names_to = "colonna", values_to = "quota") |>
  inner_join(STATI, by = "colonna") |>
  mutate(stato = factor(nome, levels = STATI$nome)) |>
  # La riga vuota del 2020 serve al controllo di buco_2020(): senza, la figura
  # racconterebbe una serie continua dove la fonte ha un buco.
  complete(stato, anno = 2018:2024)

stopifnot(nrow(serie) == nrow(STATI) * 7)

# Le quote sommano a 100 in ogni annata rilevata: se la pipeline cambiasse la definizione
# di uno stato la pila mentirebbe in silenzio sul totale.
totali <- serie |>
  filter(!is.na(quota)) |>
  summarise(totale = sum(quota), .by = anno)
stopifnot(all(abs(totali$totale - 100) < 0.01), nrow(totali) == 6)

# `geom_area` non sa cosa fare della riga vuota: la si toglie qui e la striscia opaca
# copre il tratto in cui il poligono attraversa il buco.
disegnabile <- filter(serie, !is.na(quota))

# Il confine fra "in cerca" e "occupati" È l'aggregato del claim: sotto quella linea sta
# chi è fuori da lavoro e studio. Tracciarla evita che il lettore debba sommare due bande.
fuori <- select(stati, anno, quota = quota_fuori_lavoro_studio)

# Le etichette di banda vanno al centro verticale della propria banda, che nella pila è
# il cumulato meno metà dello spessore. Si calcola sull'ordine della pila, non a mano.
centro_banda <- function(d) {
  d |>
    arrange(desc(stato)) |>
    mutate(alto = cumsum(quota), y = alto - quota / 2)
}

primo <- centro_banda(filter(disegnabile, anno == min(anno)))
ultimo <- centro_banda(filter(disegnabile, anno == max(anno)))

quota_di <- function(nome_stato, a) {
  disegnabile$quota[disegnabile$stato == nome_stato & disegnabile$anno == a]
}

figura <- ggplot(disegnabile, aes(asse_2020(anno), quota, fill = stato)) +
  geom_area(colour = "white", linewidth = 0.5) +
  # Il confine dell'aggregato, sopra le aree: è una linea di lettura, non una serie in più.
  geom_line(data = fuori, aes(asse_2020(anno), quota), inherit.aes = FALSE,
            linewidth = 0.9, colour = "grey15", linetype = "22") +
  geom_text(data = primo, aes(y = y, label = virgola(quota, 1, "%")),
            hjust = 0, nudge_x = 0.07, size = 3.2, fontface = "bold", colour = "white",
            show.legend = FALSE) +
  geom_text(data = ultimo, aes(y = y, label = virgola(quota, 1, "%")),
            hjust = 1, nudge_x = -0.07, size = 3.2, fontface = "bold", colour = "white",
            show.legend = FALSE) +
  annotate("text", x = asse_2020(2022), y = 29.4, hjust = 0.5, vjust = 0, size = 3.1,
           colour = "grey15", fontface = "bold",
           label = "sotto la linea: fuori da lavoro e studio") +
  scale_fill_manual(values = setNames(STATI$colore, STATI$nome), name = NULL) +
  scala_2020() +
  scale_y_continuous(breaks = seq(0, 100, 20),
                     labels = function(x) virgola(x, 0, "%")) +
  # L'inquadratura si fissa con coord_cartesian, non con `limits` sulla scala: `limits`
  # censura i valori fuori range PRIMA dell'impilamento, e la cima della pila vale 100
  # con l'errore di virgola mobile — con `limits = c(0, 100)` la banda degli studenti
  # veniva scartata e geom_area falliva sul gruppo rimasto vuoto.
  coord_cartesian(ylim = c(0, 100), expand = FALSE) +
  buco_2020(50, serie$anno, serie$quota) +
  labs(
    title = "Fra i giovani di Bagheria si svuota la ricerca di lavoro, mentre l'inattività tiene",
    subtitle = sommario(paste0(
      "Composizione della condizione professionale dei 15-24enni di Bagheria, in percentuale della popolazione della classe, dal ",
      ANNI_STATI[1], " al ", ANNI_STATI[2],
      ": i quattro stati sono esaustivi e si escludono a vicenda, quindi sommano al 100% in ogni annata rilevata. ",
      "La pila è appoggiata sugli inattivi non studenti, cioè il segmento di cui parla il claim, perché nella pila solo la banda che tocca lo zero ha uno spessore confrontabile fra annate.\n",
      "Sopra ci sta chi cerca lavoro: insieme sono l'area \"fuori da lavoro e studio\", il cui bordo superiore è la linea tratteggiata, ",
      "e che è la somma dei due stati alla base e non un quinto stato. In sei anni la quota di chi cerca crolla dal ",
      virgola(quota_di("in cerca di lavoro", 2018), 1), "% al ",
      virgola(quota_di("in cerca di lavoro", 2024), 1), "%,\n",
      "mentre gli inattivi non studenti passano dal ",
      virgola(quota_di("inattivi non studenti", 2018), 1), "% al ",
      virgola(quota_di("inattivi non studenti", 2024), 1),
      "%: la banda alla base è la stessa di sei anni fa."), LARGHEZZA),
    x = NULL, y = "quota dei 15-24enni residenti",
    caption = didascalia_2b(
      lettura = paste0(
        "la pila è appoggiata sugli inattivi non studenti, cioè il segmento di cui parla il claim, così che la sua banda parta dalla linea di base e il suo spessore si legga senza doverlo misurare a metà pila. ",
        "Lo spessore verticale di ogni banda in un'annata è la quota di quello stato in quell'anno. ",
        "Le etichette numeriche riportano la prima e l'ultima annata, mentre le intermedie si leggono sullo spessore delle bande. ",
        "La striscia grigia verticale occupa l'annata mancante: l'asse si comprime, dove c'è la striscia non c'è misura, e il 2020 non è interpolato. ",
        "Poiché la composizione somma sempre a 100, una banda che si assottiglia può farlo perché quel gruppo si riduce o perché un altro cresce: la scomposizione fra i due effetti sta in edu_fig04. ",
        "«Inattivi non studenti» sono i 15-24enni che non lavorano, non cercano e non sono in istruzione: vanno letti per quello, non come il NEET ISTAT 15-29, che a livello comunale non è calcolabile su queste annate."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, ",
        ANNI_STATI[1], "-", ANNI_STATI[2], " (", migliaia(round(enne_anno(ANNI_STATI[1]))), " residenti nel ",
        ANNI_STATI[1], " e ", migliaia(round(enne_anno(ANNI_STATI[2]))), " nel ", ANNI_STATI[2],
        "). Elaborazione: pipeline/edu (thread educazione), data/processed/edu_youth_states_2018_2024.csv."),
      larghezza = LARGHEZZA)
  ) +
  tema_figura()

salva(figura, "edu_fig03_composizione", larghezza = LARGHEZZA, altezza = 21)
