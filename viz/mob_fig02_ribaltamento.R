# Mobilità, figura 2 — il ribaltamento: le ragazze escono per studiare, le donne non
# escono per lavorare. È il risultato del thread, e la figura deve reggerlo da sola.
# Sinistra: le due misure per territorio, unite da una linea la cui pendenza È il finding.
# Destra: dove cade Bagheria nella distribuzione dei 390 comuni siciliani.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 28

territori <- read_csv(file.path(PROCESSED, "mob_ribaltamento.csv"),
                      col_types = cols(territorio = "c", motivo = "c", .default = "d"))
larghi <- read_csv(file.path(PROCESSED, "mob_ribaltamento_territori.csv"),
                   col_types = cols(territorio = "c", .default = "d"))
comuni <- read_csv(file.path(PROCESSED, "mob_ribaltamento_390.csv"),
                   col_types = cols(territorio = "c", nome = "c", .default = "d"))
# I pendolari di Bagheria: la base su cui poggiano le quote del pannello di sinistra.
pendolari <- read_csv(file.path(PROCESSED, "mob_treno_390.csv"), show_col_types = FALSE)
N_BAGHERIA <- pendolari$pendolari[pendolari$territorio == "082006"]

# Il controllo su una rilevazione diversa: la stessa misura sul censimento permanente,
# letta dal file invece che ricopiata a mano nel sottotitolo.
controllo <- read_csv(file.path(PROCESSED, "genere_pendolarismo.csv"), show_col_types = FALSE) |>
  filter(anno == min(anno)) |>
  select(nome_territorio, motivo, gap_M_meno_F) |>
  pivot_wider(names_from = motivo, values_from = gap_M_meno_F) |>
  mutate(ribaltamento = (-STD) - (-WK))
ANNO_CONTROLLO <- min(read_csv(file.path(PROCESSED, "genere_pendolarismo.csv"),
                               show_col_types = FALSE)$anno)
ctrl <- function(t) virgola(controllo$ribaltamento[controllo$nome_territorio == t], 1)

ORDINE_T <- larghi$territorio           # già ordinato dal notebook: Bagheria per prima
BAG <- "082006"
bagheria <- filter(comuni, territorio == BAG)

# --- pannello A: la pendenza ----------------------------------------------------------
# Un punto per motivo, la linea che li unisce. Il colore distingue Bagheria dal contesto:
# gli altri quattro territori sono lì per dire che il ribaltamento esiste ovunque e che
# quello che cambia è l'ampiezza — se fossero colorati uno per uno, la figura racconterebbe
# cinque storie invece di una.
lungo <- larghi |>
  pivot_longer(c(gap_studio_F_M, gap_lavoro_F_M), names_to = "motivo", values_to = "gap") |>
  mutate(motivo = factor(if_else(motivo == "gap_studio_F_M", "per studiare", "per lavorare"),
                         levels = c("per studiare", "per lavorare")),
         soggetto = territorio == "Bagheria",
         territorio = factor(territorio, levels = rev(ORDINE_T)))

etichette_dx <- filter(lungo, motivo == "per lavorare") |>
  arrange(gap) |> mutate(y_lab = scosta_etichette(gap, 1.35))
etichette_sx <- filter(lungo, motivo == "per studiare") |>
  arrange(gap) |> mutate(y_lab = scosta_etichette(gap, 1.3))

pendenza <- ggplot(lungo, aes(motivo, gap, group = territorio)) +
  # Chiara: una delle etichette di destra finisce quasi sulla riga dello zero, e a
  # grey40 la riga ci passava sopra rendendola illeggibile.
  geom_hline(yintercept = 0, colour = "grey78", linewidth = 0.4) +
  geom_line(aes(colour = soggetto, linewidth = soggetto)) +
  geom_point(aes(colour = soggetto, size = soggetto)) +
  # Quattro dei cinque territori arrivano quasi allo stesso valore su entrambi i lati, e
  # le scritte finivano una sopra l'altra: scosta_etichette() le separa quel tanto che
  # basta. Lo scostamento tocca solo il testo — i punti restano sul valore vero — ed è
  # dichiarato in caption.
  geom_text(data = etichette_dx,
            aes(y = y_lab, label = paste0(territorio, "  ", virgola(gap, 1)), colour = soggetto,
                fontface = if_else(soggetto, "bold", "plain")),
            hjust = 0, nudge_x = 0.06, size = 3.2) +
  geom_text(data = etichette_sx, aes(y = y_lab, label = virgola(gap, 1), colour = soggetto),
            hjust = 1, nudge_x = -0.06, size = 3.2) +
  annotate("text", x = 1.5, y = 9, size = 3.1, colour = "grey35", lineheight = 1.05,
           label = paste0("il salto di Bagheria:\n",
                          virgola(larghi$ribaltamento[1], 1), " punti")) +
  annotate("segment", x = 1.5, xend = 1.5, y = 7.4,
           yend = mean(c(larghi$gap_studio_F_M[1], larghi$gap_lavoro_F_M[1])) + 1.4,
           colour = "grey45", linewidth = 0.3,
           arrow = arrow(length = unit(0.15, "cm"), type = "closed")) +
  scale_colour_manual(values = c(`TRUE` = COLORI_TERRITORIO[["Bagheria"]], `FALSE` = "grey55"),
                      guide = "none") +
  scale_linewidth_manual(values = c(`TRUE` = 1.4, `FALSE` = 0.5), guide = "none") +
  scale_size_manual(values = c(`TRUE` = 3, `FALSE` = 1.8), guide = "none") +
  # Il margine destro tiene la scritta più lunga («Comune di Palermo  −2,0»): con meno
  # spazio veniva tagliata dal bordo del pannello, e il taglio non lo segnala nessuno.
  scale_x_discrete(expand = expansion(mult = c(0.20, 0.78))) +
  scale_y_continuous(labels = function(y) virgola(y, 0)) +
  labs(subtitle = "Lo scarto cambia segno col motivo, ovunque",
       x = NULL, y = "chi esce dal comune, F − M (punti %)") +
  theme(panel.grid.major.x = element_blank())

# --- pannello B: i 390 comuni ---------------------------------------------------------
# L'istogramma dice che il ribaltamento non è una stranezza di Bagheria: è la norma. Quello
# che Bagheria ha di suo è la coda in cui sta.
percentile <- 100 * mean(comuni$ribaltamento < bagheria$ribaltamento)
mediana <- median(comuni$ribaltamento)

distribuzione <- ggplot(comuni, aes(ribaltamento)) +
  geom_histogram(binwidth = 2, fill = "grey80", colour = "white", linewidth = 0.2) +
  geom_vline(xintercept = mediana, colour = "grey35", linewidth = 0.6) +
  geom_vline(xintercept = bagheria$ribaltamento, colour = COLORI_TERRITORIO[["Bagheria"]],
             linewidth = 1) +
  annotate("text", x = mediana - 1.5, y = 62, hjust = 1, size = 3.1, colour = "grey30",
           lineheight = 1.05,
           label = paste0("mediana dei 390 comuni\n", virgola(mediana, 1), " punti")) +
  annotate("text", x = bagheria$ribaltamento + 1.5, y = 62, hjust = 0, size = 3.1,
           fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]], lineheight = 1.05,
           label = paste0("Bagheria ", virgola(bagheria$ribaltamento, 1), "\n",
                          virgola(percentile, 0, "° percentile"))) +
  scale_x_continuous(labels = function(x) virgola(x, 0)) +
  coord_cartesian(xlim = c(-25, 40), clip = "off") +
  labs(subtitle = "Il ribaltamento è la norma: Bagheria è nella coda",
       x = "ribaltamento (punti %): scarto studio meno scarto lavoro", y = "comuni") +
  theme(panel.grid.major.x = element_blank())

figura <- (pendenza | distribuzione) +
  plot_layout(widths = c(1.05, 1)) +
  plot_annotation(
    title = "Le ragazze di Bagheria si spostano per studiare. Le donne non si spostano per lavorare",
    subtitle = paste0(
      "Fra chi già si sposta per studiare escono dal comune ", virgola(larghi$gap_studio_F_M[1], 1),
      " punti più femmine che maschi. Fra chi si sposta per lavorare, ",
      virgola(abs(larghi$gap_lavoro_F_M[1]), 1), " punti meno donne che uomini.\n",
      "Il salto fra le due misure vale ", virgola(larghi$ribaltamento[1], 1),
      " punti a Bagheria, contro ", virgola(larghi$ribaltamento[larghi$territorio == 'Sicilia'], 1),
      " in Sicilia e ", virgola(larghi$ribaltamento[larghi$territorio == 'Italia'], 1), " in Italia: due volte e mezza.\n",
      "Il denominatore è già condizionato al motivo (chi si sposta per lavoro un lavoro ce l'ha), ",
      "quindi non è il divario occupazionale visto da un'altra angolazione,\n",
      "ma una misura indipendente sullo stesso passaggio.\n",
      "La stessa misura sul censimento permanente del ", ANNO_CONTROLLO,
      ", cioè un'altra rilevazione sette anni dopo, dà per Bagheria +", ctrl("Bagheria"),
      " contro +", ctrl("Sicilia"), " siciliano."),
    caption = didascalia_4b(
      mostra = paste0(
        "scarto fra femmine e maschi nella propensione a uscire dal comune, misurato separatamente per i due motivi dello spostamento. ",
        "La misura è la quota di chi esce dal comune sul totale di chi si sposta quotidianamente per quel motivo, calcolata per genere; il valore riportato è femmine meno maschi, in punti percentuali. ",
        "Il pannello di sinistra confronta cinque territori sui due motivi; quello di destra colloca Bagheria nella distribuzione dei 390 comuni siciliani del «ribaltamento», cioè lo scarto sullo studio meno lo scarto sul lavoro. ",
        "Il denominatore è già condizionato al motivo, perché chi si sposta per lavoro un lavoro ce l'ha: non è quindi il divario occupazionale visto da un'altra angolazione, ma una misura indipendente sullo stesso passaggio."),
      base = paste0(
        "N = ", migliaia(round(N_BAGHERIA)), " pendolari a Bagheria e 390 comuni siciliani ai confini del 2011, l'universo usato da tutti i thread del progetto. ",
        "Conteggio esaustivo da matrice origine-destinazione (record di tipo S): non è una stima campionaria, non ha errore di campionamento e non porta intervallo di confidenza. Nessuna esclusione. ",
        "La matrice non ha la dimensione dell'età: il target 15-34 del bando non è isolabile su questa fonte. Chi esce dal comune per studio è però quasi solo secondaria superiore e università, perché a Bagheria i cicli precedenti ci sono tutti. ",
        "Controllo su una rilevazione indipendente: la stessa misura sul censimento permanente del ", ANNO_CONTROLLO,
        " dà ", ctrl("Bagheria"), " punti a Bagheria contro ", ctrl("Sicilia"), " in Sicilia, quindi il segno e l'ordine di grandezza si replicano sette anni dopo con un altro disegno di rilevazione. ",
        "Nessun test di significatività: con un conteggio esaustivo il confronto è fra popolazioni, non fra stime."),
      lettura = paste0(
        "nel pannello di sinistra ogni linea è un territorio e la sua pendenza è il finding: unisce lo scarto sullo studio a quello sul lavoro, e il cambio di segno è il ribaltamento. ",
        "Bagheria è in vermiglio e a tratto spesso, gli altri quattro territori sono grigi perché servono a mostrare che il ribaltamento esiste ovunque e che quello che cambia è l'ampiezza. ",
        "La riga orizzontale chiara è lo zero, cioè la parità fra i generi. Le etichette di fine linea sono scostate in verticale quel tanto che basta a non sovrapporsi: i punti stanno sul valore vero, le scritte no. ",
        "Nel pannello di destra ogni barra conta i comuni con quel valore di ribaltamento; la riga grigia è la mediana dei 390 comuni e quella vermiglia è Bagheria, con il suo percentile. ",
        "«5 comuni vicini» è l'aggregato di Santa Flavia, Ficarazzi, Villabate, Casteldaccia e Misilmeri."),
      fonte = paste0(
        "ISTAT, Matrice del pendolarismo, censimento della popolazione 2011, più il Censimento permanente della popolazione del ",
        ANNO_CONTROLLO, " per il controllo. ",
        "Elaborazione: notebooks/mobilita.ipynb (data/processed/mob_ribaltamento.csv, mob_ribaltamento_territori.csv, mob_ribaltamento_390.csv, mob_treno_390.csv per i denominatori e genere_pendolarismo.csv per il controllo)."),
      larghezza = LARGHEZZA),
    theme = tema_figura())

salva(figura, "mob_fig02_ribaltamento", larghezza = LARGHEZZA, altezza = 22)
