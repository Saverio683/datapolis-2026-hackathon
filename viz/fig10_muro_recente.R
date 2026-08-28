# Figura 10 — il muro è recente, e nel 2024 è ancora aperto.
# A sinistra la posizione di Bagheria nella distribuzione dei 390 comuni siciliani: i tre
# censimenti decennali 1991-2011 e poi il censimento permanente 2018-2024, due blocchi
# separati da uno stacco perché sono due rilevazioni diverse. A destra il confronto con le
# dieci gemelle strutturali sullo stesso indicatore, con la stessa struttura.
# Il punto per la proposal: la frattura è databile (decennio 2001-2011) e **non si è
# richiusa** — tredici anni dopo Bagheria è ancora sotto le sue gemelle. Quindi non è un
# tratto immutabile del territorio, ma nemmeno qualcosa che si sistema da solo.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

madri <- read_csv(file.path(PROCESSED, "genere_gap_madri.csv"), show_col_types = FALSE)
madri_recente <- read_csv(file.path(PROCESSED, "genere_madri_recente.csv"), show_col_types = FALSE)
gemelle <- read_csv(file.path(PROCESSED, "genere_pretrend_gemelle.csv"), show_col_types = FALSE)
gemelle_recente <- read_csv(file.path(PROCESSED, "genere_pretrend_gemelle_recente.csv"),
                            show_col_types = FALSE)
# La frattura vista dall'istruzione: uscita precoce dal sistema scolastico, 1991-2011.
# Non entra nel pannello dei percentili come quinta linea per due motivi indipendenti.
# Primo, il verso è opposto a quello delle linee che ci stanno (qui alto = peggio), e su
# un asse condiviso una linea che sale significherebbe due cose diverse a seconda di
# quale si guarda. Secondo, la fonte si ferma al 2011: varrebbe la stessa obiezione già
# scritta sotto per il differenziale educativo. Sta quindi in una striscia sua, con scala
# e verso dichiarati, allineata allo stesso asse del tempo.
frattura <- read_csv(file.path(PROCESSED, "genere_frattura_istruzione.csv"),
                     show_col_types = FALSE)
stopifnot(nrow(frattura) == 3, all(frattura$anno <= 2011))

# Le due fonti non si uniscono mai in una linea sola: `epoca` entra nel `group` di ogni
# geom, così fra il 2011 e il 2018 il tracciato si interrompe invece di interpolare un
# salto che nessuno ha misurato. Vale per le linee e per la banda delle gemelle.
DECENNALE <- "censimenti 1991-2011"
PERMANENTE <- "censimento permanente 2018-2024"

# L'asse del tempo non è in scala, ed è una scelta. A scala reale i venti anni dei
# censimenti decennali si prendono due terzi della larghezza per portare tre punti, e i
# sei anni del permanente - dove stanno sei rilevazioni e la parte recente del racconto -
# si schiacciano contro il bordo destro. Qui il primo tratto è compresso e il secondo
# allungato, così lo spazio va dove stanno i dati.
# Si può fare perché le due epoche non sono già una serie sola: nessuna linea attraversa
# lo stacco, quindi non c'è nessuna pendenza continua da falsare. Restano confrontabili
# le pendenze DENTRO ciascuna epoca, che è quello che la figura chiede di leggere; fra
# un'epoca e l'altra no, e la caption lo dice.
ANNI_PER_UNITA <- 3.3   # 1991-2011: venti anni in sei unità d'asse
UNITA_PER_ANNO <- 1.2   # 2018-2024: ogni anno vale un'unità e un quinto
FINE_DECENNALE <- (2011 - 1991) / ANNI_PER_UNITA
LARGHEZZA_STACCO <- 2   # il vuoto fra le due epoche, in unità d'asse
INIZIO_PERMANENTE <- FINE_DECENNALE + LARGHEZZA_STACCO

#' Dall'anno alla posizione sull'asse. Monotona: l'ordine temporale non cambia mai, e
#' ogni annotazione ancorata a un anno passa di qui invece di portarsi dietro un numero.
asse <- function(anno) ifelse(anno <= 2011,
                              (anno - 1991) / ANNI_PER_UNITA,
                              INIZIO_PERMANENTE + (anno - 2018) * UNITA_PER_ANNO)

ANNI_ASSE <- c(1991, 2001, 2011, 2018, 2024)   # solo gli estremi delle due epoche
STACCO <- FINE_DECENNALE + LARGHEZZA_STACCO / 2   # ci vive il marcatore di frattura

marcatore_fonti <- function(y) {
  list(
    annotate("rect", xmin = FINE_DECENNALE + 0.35, xmax = INIZIO_PERMANENTE - 0.35,
             ymin = -Inf, ymax = Inf, fill = "grey95"),
    # verticale dentro la banda: orizzontale sarebbe più largo della banda stessa e
    # finirebbe sopra le curve delle due epoche.
    annotate("text", x = STACCO, y = y, size = 2.7, colour = "grey45", angle = 90,
             label = "fonte diversa - nessuna linea attraversa")
  )
}

#' Asse x comune ai due pannelli: le etichette restano gli anni, le posizioni no.
#' `margine` è lo spazio a destra per le etichette di fine linea, in unità d'asse.
scala_tempo <- function(margine) {
  scale_x_continuous(breaks = asse(ANNI_ASSE), labels = ANNI_ASSE,
                     limits = c(asse(1991), asse(2024) + margine),
                     expand = expansion(mult = c(0.03, 0)))
}

# Nomi corti per l'etichetta a fine linea (quelli per esteso stanno in `nome_indicatore`)
# e scostamento verticale dove due linee arrivano all'ultimo anno troppo vicine per due
# etichette. È impaginazione: nessun valore viene toccato, si sposta solo il testo.
# L2 e L11 nel 2024 valgono lo stesso percentile: si separano con lo scarto, che sposta
# il testo e non il dato. Il differenziale educativo M/F (I1) non è in figura perché
# esiste solo fino al 2011 e una linea che muore a metà pannello confonde: sta in caption.
ETICHETTE <- tribble(
  ~indicatore, ~breve,               ~scarto,
  "L2",        "partecipazione F",     -3.5,
  "L11",       "occupazione F",         3.5,
  "L10",       "occupazione M",         3.0,
  "L7",        "disoccupazione F",      0.0
)

# Emphasis, non una palette categorica: il finding è che l'occupazione maschile risale e
# quella femminile no, le altre curve sono contesto e restano grigie.
COLORI_INDICATORE <- c(L11 = "#D55E00", L10 = "#0072B2",
                       L2 = "#9C9C9C", L7 = "#9C9C9C")

percentili <- bind_rows(
  madri |> mutate(epoca = DECENNALE),
  madri_recente |> select(any_of(names(madri))) |> mutate(epoca = PERMANENTE)
) |>
  filter(indicatore %in% names(COLORI_INDICATORE)) |>
  left_join(ETICHETTE, by = "indicatore") |>
  mutate(indicatore = factor(indicatore, levels = names(COLORI_INDICATORE)),
         x = asse(anno))

ultimo <- percentili |> slice_max(anno, n = 1, by = indicatore)
anni <- sort(unique(percentili$anno))

posizione <- ggplot(percentili, aes(x, percentile_390, colour = indicatore)) +
  marcatore_fonti(y = 50) +
  geom_hline(yintercept = 50, colour = "grey80", linewidth = 0.4) +
  # nel margine destro, dove vivono le etichette di fine linea: dentro il pannello
  # incrocerebbe l'occupazione maschile, che proprio lì attraversa il 50.
  annotate("text", x = asse(max(anni)), y = 50, hjust = -0.09, vjust = 0.5, size = 3,
           colour = "grey45", label = "50 = mediana regionale") +
  geom_line(aes(group = interaction(indicatore, epoca),
                linewidth = indicatore %in% c("L11", "L10")), lineend = "round") +
  geom_point(size = 2.2) +
  geom_text(data = ultimo,
            aes(y = percentile_390 + scarto,
                label = paste0(breve, "  ", virgola(percentile_390, 0, "°"))),
            hjust = -0.09, size = 3.1, fontface = "bold") +
  scale_colour_manual(values = COLORI_INDICATORE, guide = "none") +
  scale_linewidth_manual(values = c(`TRUE` = 1.5, `FALSE` = 0.7), guide = "none") +
  scala_tempo(margine = 5.1) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 25)) +
  coord_cartesian(clip = "off") +
  labs(subtitle = paste0("Bagheria nella distribuzione siciliana\n",
                         "percentile sui 390 comuni, ", min(anni), "-", max(anni)),
       # Corto di proposito: il sottotitolo dice già su quanti comuni, e con la striscia
       # sotto il pannello è più basso — la scritta ruotata per esteso saliva nel titolo.
       x = NULL, y = "percentile")

# --- striscia sotto il pannello A: la stessa frattura, vista dall'istruzione ---------
# Tre punti e nient'altro: serve a datare, non a quantificare. La scala parte poco sotto
# la mediana regionale perché il salto da leggere è "da sopra la mediana a quasi in
# fondo", e il verso sta nel titolo della striscia, dove il lettore lo incontra prima
# dei numeri.
striscia <- ggplot(frattura, aes(asse(anno), percentile_390)) +
  geom_hline(yintercept = 50, colour = "grey80", linewidth = 0.4) +
  geom_line(colour = "grey45", linewidth = 0.9) +
  geom_point(colour = "grey45", size = 2.4) +
  geom_text(aes(label = virgola(percentile_390, 0, "°")),
            vjust = -1.05, size = 3.1, fontface = "bold", colour = "grey25") +
  # Dove finisce la fonte lo dice il testo, così la linea non ha bisogno di fingere.
  annotate("text", x = asse(2011) + 0.45, y = 62, hjust = 0, vjust = 0.5, size = 2.9,
           colour = "grey45", lineheight = 1.05,
           label = "8milaCensus si ferma al 2011:\nil permanente non pubblica\nquesto indicatore") +
  scala_tempo(margine = 5.1) +
  scale_y_continuous(limits = c(45, 100), breaks = c(50, 75, 100)) +
  coord_cartesian(clip = "off") +
  labs(subtitle = paste0("E la stessa frattura, vista dall'istruzione\n",
                         "uscita precoce dalla scuola - più alto = peggio"),
       x = NULL, y = "percentile")

# --- pannello B: Bagheria dentro il gruppo delle gemelle strutturali -----------------
banda <- bind_rows(
  gemelle |> mutate(epoca = DECENNALE),
  gemelle_recente |> select(-fonte) |> mutate(epoca = PERMANENTE)
) |>
  mutate(x = asse(anno))
finale <- filter(banda, anno == max(anno))
scarto_2011 <- with(filter(banda, anno == 2011), bagheria - gemelle_mediana)
scarto_finale <- finale$bagheria - finale$gemelle_mediana

confronto <- ggplot(banda, aes(x, group = epoca)) +
  marcatore_fonti(y = 19) +
  geom_ribbon(aes(ymin = gemelle_q1, ymax = gemelle_q3), fill = "grey88") +
  geom_line(aes(y = gemelle_mediana), colour = "grey45", linewidth = 0.9) +
  geom_point(aes(y = gemelle_mediana), colour = "grey45", size = 2.2) +
  geom_line(aes(y = bagheria), colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 1.5) +
  geom_point(aes(y = bagheria), colour = COLORI_TERRITORIO[["Bagheria"]], size = 2.8) +
  annotate("text", x = asse(2024) + 0.3, y = finale$bagheria,
           hjust = 0, vjust = 1.1, size = 3.2, fontface = "bold",
           colour = COLORI_TERRITORIO[["Bagheria"]], label = "Bagheria") +
  annotate("text", x = asse(2024) + 0.3, y = finale$gemelle_mediana,
           hjust = 0, vjust = -0.15, size = 3.2, fontface = "bold", colour = "grey35",
           label = "mediana\ndelle 10 gemelle") +
  annotate("text", x = asse(1991), y = 20.5, hjust = 0, vjust = 1, size = 3.1,
           colour = "grey35", label = "identiche nel 1991\ne nel 2001") +
  # Nel tratto compresso i due blocchi di testo non ci stanno più affiancati: questo sale
  # sopra la banda, nello spazio vuoto in alto a sinistra, e la freccia scende sul 2011.
  annotate("text", x = asse(1991), y = 26.8, hjust = 0, vjust = 1, size = 3.1,
           colour = "grey35", lineheight = 1.05,
           label = paste0("si stacca nel decennio\n2001-2011 (", virgola(scarto_2011), " punti)")) +
  annotate("segment", x = asse(2004), xend = asse(2010.6), y = 24.4, yend = 21.0,
           colour = "grey45", linewidth = 0.35,
           arrow = arrow(length = unit(0.16, "cm"), type = "closed")) +
  annotate("text", x = asse(2024) + 3.9, y = 13.5, hjust = 1, size = 3.1,
           colour = "grey35", lineheight = 1.05,
           label = paste0("e non si è chiuso:\n", virgola(scarto_2011), " punti nel 2011,\n",
                          virgola(scarto_finale), " nel 2024")) +
  scala_tempo(margine = 4.1) +
  coord_cartesian(clip = "off") +
  labs(subtitle = paste0("Bagheria dentro il suo gruppo di pari\n",
                         "occupazione femminile 15+, banda = 1°-3° quartile"),
       x = NULL, y = "tasso di occupazione femminile (%)")

figura <- ((posizione / striscia + plot_layout(heights = c(1, 0.32))) | confronto) +
  plot_layout(widths = c(1.15, 1)) +
  plot_annotation(
    title = "Il muro si alza fra il 2001 e il 2011, e nel 2024 è ancora lì",
    subtitle = paste0(
      "Fra il 1991 e il 2011 le donne di Bagheria entrano nel lavoro, ma il mercato non le assorbe: l'occupazione femminile scende al 12° percentile.\n",
      "Il censimento permanente mostra che dopo il 2011 è peggiorata ancora - 8° percentile nel 2018 - e che al 2024 ha recuperato solo in parte, al 17°.\n",
      "Fra il 2011 e il 2024 l'occupazione maschile risale dal 15° al 30° percentile, mentre la partecipazione femminile continua a scendere, dal 32° al 17°:\n",
      "la lettura del 2011, un mercato ristretto per tutti, al 2024 non regge più - gli uomini recuperano e le donne no.\n",
      "Rispetto alle gemelle strutturali lo scarto non si è chiuso: -1,7 punti nel 2011, fra -2,1 e -3,1 in ogni anno dal 2018 al 2024.\n",
      "Nello stesso decennio peggiora anche l'istruzione, e in modo indipendente dal lavoro: l'uscita precoce dalla scuola passa dal ",
      virgola(frattura$percentile_390[frattura$anno == 2001], 0, "°"), " al ",
      virgola(frattura$percentile_390[frattura$anno == 2011], 0, "° percentile"), ".\n",
      "Due domini diversi, due indicatori diversi, la stessa datazione: il 2001-2011 non è un artefatto della misura del lavoro.\n",
      "Per la proposal: la frattura è databile e non si richiude da sola - e il pre-periodo del disegno di valutazione adesso è misurato, non assunto."),
    caption = paste0(
      "Fonte: ISTAT - 8milaCensus (censimenti 1991, 2001, 2011) e Censimento permanente (2018-2024, il 2020 manca alla fonte). Popolazione 15 anni e più.\n",
      "L'asse del tempo non è in scala: 1991-2011 compresso, 2018-2024 allungato, per dare spazio agli anni con più rilevazioni. Le pendenze si leggono dentro ciascuna epoca, non fra le due.\n",
      "Due rilevazioni con disegni diversi: universale a questionario la prima, campionaria sui registri la seconda. Nessuna linea attraversa lo stacco fra le due epoche.\n",
      "Il percentile è un rango calcolato dentro l'anno, quindi assorbe lo scarto di definizione fra le fonti; i livelli assoluti no, e infatti nel pannello destro le due epoche restano separate.\n",
      "Cautela su partecipazione e disoccupazione femminile: fra il 2019 e il 2021 il permanente cambia la misura di 'in cerca di occupazione' (a Bagheria la disoccupazione F cala di 15,5 punti, in Italia di 4,5).\n",
      "Occupazione maschile e femminile non ne risentono. Il differenziale educativo M/F si ferma al 2011: 8milaCensus lo calcola sulla popolazione 6+, il permanente non ha una classe 15+ sull'istruzione.\n",
      "390 comuni ai confini 2011 in entrambe le epoche (Misiliscemi, istituito nel 2021, resta fuori per non cambiare il denominatore).\n",
      "Gemelle = i 10 comuni più simili a Bagheria per dimensione, densità, età, stranieri, abitazioni e distanza da Palermo (matching Mahalanobis su variabili non-esito, nel notebook).\n",
      "L'uscita precoce (indicatore I5, 8milaCensus) è la quota di 15-24enni con la sola licenza media fuori da scuola e formazione: verso opposto al pannello sopra, per questo ha scala e striscia sue.\n",
      "I suoi percentili, ricalcolati in questo thread, coincidono con quelli del thread educazione su tutte e 18 le coppie indicatore x anno (scarto massimo 0,00).\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_gap_madri.csv, genere_madri_recente.csv, genere_pretrend_gemelle.csv, genere_pretrend_gemelle_recente.csv, genere_frattura_istruzione.csv"),
    theme = tema_figura()
  )

salva(figura, "fig10_muro_recente", larghezza = 29, altezza = 21)
