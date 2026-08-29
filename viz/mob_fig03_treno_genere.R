# Mobilità, figura 3 — come si esce da Bagheria, e perché il treno è un fatto di genere.
# Tre pannelli che rispondono a tre domande diverse sulla stessa popolazione:
#   A  con che mezzo   -> le donne sul collettivo, gli uomini in auto
#   B  a che ora       -> gli uomini prima delle 7:15, le donne nella fascia dopo
#   C  e rispetto agli altri comuni? -> Bagheria è al 97° percentile per uso del treno
# Il pannello C esiste perché senza di lui A si legge come «serve più treno»: il treno c'è
# già, più che quasi ovunque in Sicilia. È la correzione che la figura deve portare con sé.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 30

mezzo <- read_csv(file.path(PROCESSED, "mob_mezzo_genere.csv"),
                  col_types = cols(genere = "c", classe = "c", .default = "d"))
orario <- read_csv(file.path(PROCESSED, "mob_orario_genere.csv"),
                   col_types = cols(genere = "c", orario = "c", .default = "d"))
tutti_390 <- read_csv(file.path(PROCESSED, "mob_treno_390.csv"),
                      col_types = cols(territorio = "c", nome = "c", .default = "d"))

BAG <- "082006"
# Sotto le 100 uscite la quota è rumore: a Lampedusa e Linosa esce dal comune una persona
# sola, che prende il treno, e il comune risulta al 100%. Tredici comuni su 390 stanno
# sotto questa soglia; escluderli è dichiarato in caption, non nascosto.
SOGLIA <- 100
comuni <- filter(tutti_390, pendolari_fuori >= SOGLIA)
esclusi <- nrow(tutti_390) - nrow(comuni)
bagheria <- filter(comuni, territorio == BAG)
percentile <- 100 * mean(comuni$treno < bagheria$treno)

# La base delle quote del pannello A: quante persone escono davvero, per genere.
# «di cui: treno» è un sottoinsieme, quindi non entra nella somma.
enne_mezzo <- function(g) sum(mezzo$persone[mezzo$genere == g &
                                              mezzo$classe != "di cui: treno"])

# --- A: il mezzo ----------------------------------------------------------------------
# «di cui: treno» è un di-cui del collettivo, non una quinta classe: sta come barra
# staccata sotto, altrimenti la somma delle barre farebbe 130.
ORDINE_MEZZO <- c("privato a motore", "collettivo", "piedi o bici",
                  "aziendale o scolastico", "altro")
classi <- filter(mezzo, classe %in% ORDINE_MEZZO) |>
  mutate(classe = factor(classe, levels = rev(ORDINE_MEZZO)))
treno <- filter(mezzo, classe == "di cui: treno")

pannello_mezzo <- ggplot(classi, aes(quota, classe, fill = genere)) +
  geom_col(position = position_dodge(width = 0.72), width = 0.66) +
  # Sotto i due punti le due etichette si toccherebbero: là il valore si legge in asse.
  geom_text(data = filter(classi, quota >= 2), aes(label = virgola(quota, 1, "%"), colour = genere),
            position = position_dodge(width = 0.72), hjust = -0.15, size = 3) +
  scale_fill_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  scale_colour_manual(values = COLORI_GENERE, guide = "none") +
  scale_x_continuous(limits = c(0, 92), labels = function(x) virgola(x, 0, "%")) +
  labs(subtitle = paste0("A. Con che mezzo esce chi parte da Bagheria\n",
                         "il treno da solo vale ", virgola(filter(treno, genere == "F")$quota, 1, "%"),
                         " fra le donne e ", virgola(filter(treno, genere == "M")$quota, 1, "%"), " fra gli uomini"),
       x = NULL, y = NULL) +
  theme(panel.grid.major.y = element_blank())

# --- B: l'orario ----------------------------------------------------------------------
ORDINE_ORARIO <- c("prima delle 7:15", "7:15-8:14", "8:15-9:14", "dopo le 9:14")
pannello_orario <- orario |>
  mutate(orario = factor(orario, levels = rev(ORDINE_ORARIO))) |>
  ggplot(aes(quota, orario, fill = genere)) +
  geom_col(position = position_dodge(width = 0.72), width = 0.66) +
  geom_text(aes(label = virgola(quota, 1, "%"), colour = genere),
            position = position_dodge(width = 0.72), hjust = -0.15, size = 3) +
  scale_fill_manual(values = COLORI_GENERE, guide = "none") +
  scale_colour_manual(values = COLORI_GENERE, guide = "none") +
  scale_x_continuous(limits = c(0, 78), labels = function(x) virgola(x, 0, "%")) +
  labs(subtitle = paste0("B. A che ora esce di casa\n",
                         "gli uomini prima delle 7:15, le donne nella fascia successiva"),
       x = NULL, y = NULL) +
  theme(panel.grid.major.y = element_blank())

# --- C: e gli altri 390 comuni? -------------------------------------------------------
pannello_390 <- ggplot(comuni, aes(treno)) +
  geom_histogram(binwidth = 1.5, fill = "grey80", colour = "white", linewidth = 0.2) +
  geom_vline(xintercept = median(comuni$treno), colour = "grey35", linewidth = 0.6) +
  geom_vline(xintercept = bagheria$treno, colour = COLORI_TERRITORIO[["Bagheria"]],
             linewidth = 1) +
  annotate("text", x = median(comuni$treno) + 1.5, y = 150, hjust = 0, size = 3.1,
           colour = "grey30", lineheight = 1.05,
           # «non ha una stazione» sarebbe un'inferenza: il dato dice la quota d'uso,
           # non la presenza dell'infrastruttura. Si scrive quello che il dato dice.
           label = paste0("mediana: ", virgola(median(comuni$treno), 1, "%"),
                          "\nin metà dei comuni siciliani\nil treno è irrilevante")) +
  annotate("text", x = bagheria$treno - 1.2, y = 95, hjust = 1, size = 3.2, fontface = "bold",
           colour = COLORI_TERRITORIO[["Bagheria"]], lineheight = 1.05,
           label = paste0("Bagheria ", virgola(bagheria$treno, 1, "%"), "\n",
                          virgola(percentile, 0, "° percentile"))) +
  scale_x_continuous(labels = function(x) virgola(x, 0, "%")) +
  # Il massimo è Termini Imerese al 37,5%: oltre i 40 punti non c'è nessuno, e lasciare
  # l'asse fino a 100 sprecava metà pannello per rappresentare il vuoto.
  coord_cartesian(xlim = c(0, 40)) +
  labs(subtitle = paste0("C. Il treno a Bagheria è già l'asset di mobilità\n",
                         "più distintivo che il comune abbia"),
       x = "quota di chi esce dal comune che usa il treno", y = "comuni") +
  theme(panel.grid.major.x = element_blank())

figura <- (pannello_mezzo / pannello_orario | pannello_390) +
  plot_layout(widths = c(1.15, 1)) +
  plot_annotation(
    title = "Le donne di Bagheria raggiungono Palermo in treno. Gli uomini in auto",
    subtitle = paste0(
      "Tre letture della stessa popolazione, i residenti di Bagheria che escono dal comune: il pannello A dà\n",
      "la composizione per mezzo di trasporto, in percentuale degli spostamenti di ciascun genere, il pannello B\n",
      "la distribuzione per fascia oraria di uscita da casa, il pannello C la posizione di Bagheria nella\n",
      "distribuzione siciliana dell'uso del treno. Il pannello C è parte della lettura e non un'appendice: senza,\n",
      "il pannello A si leggerebbe come «serve più treno», mentre il treno a Bagheria c'è già più che quasi\n",
      "ovunque in Sicilia.\n",
      "Fra chi esce dal comune, il mezzo collettivo vale il ",
      virgola(filter(classi, genere == "F", classe == "collettivo")$quota, 1, "%"),
      " degli spostamenti delle donne e il ",
      virgola(filter(classi, genere == "M", classe == "collettivo")$quota, 1, "%"), " di quelli degli uomini;\n",
      "il solo treno il ", virgola(filter(treno, genere == "F")$quota, 1, "%"), " contro il ",
      virgola(filter(treno, genere == "M")$quota, 1, "%"), ". Gli uomini guidano: ",
      virgola(filter(classi, genere == "M", classe == "privato a motore")$quota, 1, "%"),
      " su mezzo privato a motore, contro il ",
      virgola(filter(classi, genere == "F", classe == "privato a motore")$quota, 1, "%"), ".\n",
      "Per le donne il servizio è il canale d'accesso più che una comodità: se l'orario non copre, l'accesso non c'è.\n",
      "Ma il pannello C sposta il vincolo altrove: di treno Bagheria ne usa già più del ",
      virgola(percentile, 0, "%"), " dei comuni siciliani.\n",
      "Il divario di genere si apre altrove: nel passaggio dallo studio al lavoro (figura 2)."),
    caption = didascalia_2b(
      lettura = paste0(
        "nei pannelli A e B il colore è il genere, rosa le donne e blu gli uomini, e le due barre affiancate della stessa riga sono i due generi sulla stessa voce. ",
        "Nel pannello A la barra «di cui: treno» è staccata dalle altre perché è un sottoinsieme della classe «collettivo» e non una quinta classe: le quattro classi sommano a 100, la barra del treno no. ",
        "Le classi seguono la convenzione di 8milaCensus, verificata ricostruendo gli indicatori M5, M6 e M7, e «collettivo» esclude l'autobus aziendale o scolastico, che è contato a parte. ",
        "Nel pannello C ogni barra conta i comuni con quel valore, la riga vermiglia è Bagheria e il percentile è scritto accanto; restano fuori i ", esclusi,
        " comuni su 390 dove escono meno di ", SOGLIA,
        " persone al giorno, perché sotto quella soglia la quota è rumore. Il percentile mostrato è quello grezzo, e a parità di distanza dal capoluogo e di dimensione il residuo di Bagheria resta al 97°. ",
        "Mezzo, orario di uscita e durata sono rilevati su CAMPIONE nei comuni sopra i 20.000 abitanti, e Bagheria è uno di questi: i valori dei pannelli A e B sono stime, calibrate sui margini esatti dei record di tipo S. ",
        "Della fascia oraria si conosce solo l'uscita di casa: del rientro la matrice non dice nulla, e l'ipotesi del carico di cura resta un'ipotesi non verificata da questi dati."),
      fonte = paste0(
        "ISTAT, Matrice del pendolarismo, censimento della popolazione 2011, su ",
        migliaia(round(enne_mezzo("F"))), " donne e ", migliaia(round(enne_mezzo("M"))),
        " uomini che escono dal comune. ",
        "Elaborazione: notebooks/mobilita.ipynb (data/processed/mob_mezzo_genere.csv, mob_orario_genere.csv e mob_treno_390.csv)."),
      larghezza = LARGHEZZA),
    theme = tema_figura())

salva(figura, "mob_fig03_treno_genere", larghezza = LARGHEZZA, altezza = 26)
