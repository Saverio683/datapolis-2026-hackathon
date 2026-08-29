# Mobilità, figura 4 — perché «Bagheria si muove poco» è una lettura sbagliata di un
# numero giusto. Il percentile grezzo di M2 dice 25°, e sembra un'anomalia; ma fuori
# comune si va per mancanza di lavoro dentro, e Bagheria è il comune più grande della
# corona di Palermo. A parità di distanza dal capoluogo e di taglia, sta nella media.
# La figura serve a togliere di mezzo un claim, non a stabilirne uno: è la ragione per cui
# sta in questo thread e non in appendice.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 28

comuni <- read_csv(file.path(PROCESSED, "mob_taglia_distanza.csv"),
                   col_types = cols(territorio = "c", nome = "c", .default = "d"))
curve <- read_csv(file.path(PROCESSED, "mob_curva_attesa.csv"),
                  col_types = cols(scenario = "c", .default = "d"))
BAG <- "082006"
bagheria <- filter(comuni, territorio == BAG)

percentile_grezzo <- 100 * mean(comuni$quota_fuori < bagheria$quota_fuori)
percentile_residuo <- 100 * mean(comuni$residuo < bagheria$residuo)

# Il vicino che il sottotitolo usa come contrasto: piccolo e con quota alta. Si legge dal
# dato invece di essere scritto a mano, così se la classifica cambia cambia anche la frase.
# Stessi filtri di `vicini_30`, che è definito più sotto per le etichette del pannello A:
# provincia di Palermo, entro 30 km dal capoluogo e con una platea che regge il confronto.
# Senza la soglia sui pendolari il massimo cade su comuni da poche centinaia di pendolari,
# dove la quota è rumore e il contrasto non dice niente.
CONTRASTO <- comuni |>
  filter(substr(territorio, 1, 3) == "082", km_capoluogo <= 30, pendolari >= 2000,
         territorio != BAG) |>
  slice_max(quota_fuori, n = 1)

# --- A: la nuvola --------------------------------------------------------------------
# Asse x logaritmico perché il modello è in log della distanza: la curva attesa deve
# apparire come la retta che è, altrimenti la figura e il modello dicono cose diverse.
# La dimensione del punto è il numero di pendolari, cioè la variabile che spiega l'apparente
# anomalia: si vede a occhio che i comuni grandi stanno in basso.
vicini_30 <- filter(comuni, km_capoluogo <= 30, substr(territorio, 1, 3) == "082",
                    pendolari >= 2000, territorio != BAG) |>
  slice_max(pendolari, n = 5)

nuvola <- ggplot(comuni, aes(km_capoluogo, quota_fuori)) +
  geom_point(aes(size = pendolari), colour = "grey70", alpha = 0.5) +
  # Due curve e non una: l'atteso dipende anche dalla taglia, quindi una linea sola
  # attraverso i punti sarebbe una spezzata senza significato. Le due curve a taglia
  # fissata mostrano proprio la cosa che spiega l'apparente anomalia — la taglia sposta
  # la curva in basso di una decina di punti.
  geom_line(data = curve, aes(km_capoluogo, atteso, linetype = scenario),
            colour = "grey25", linewidth = 0.7) +
  geom_point(data = bagheria, aes(size = pendolari),
             colour = COLORI_TERRITORIO[["Bagheria"]]) +
  geom_segment(data = bagheria, aes(xend = km_capoluogo, yend = atteso),
               colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 0.6) +
  geom_text(data = vicini_30, aes(label = nome), size = 2.8, colour = "grey40",
            hjust = 0, nudge_x = 0.6) +
  annotate("text", x = bagheria$km_capoluogo + 1.5, y = bagheria$quota_fuori - 9, hjust = 0,
           size = 3.2, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]],
           lineheight = 1.05,
           label = paste0("Bagheria\n", virgola(bagheria$quota_fuori, 1, "%"), " osservato\n",
                          virgola(bagheria$atteso, 1, "%"), " atteso")) +
  scale_size_continuous(name = "pendolari del comune", range = c(0.8, 9),
                        breaks = c(1000, 5000, 10000), labels = migliaia) +
  scale_linetype_manual(name = NULL, values = c(`comune mediano` = "solid",
                                                `taglia di Bagheria` = "22")) +
  guides(linetype = guide_legend(order = 2, override.aes = list(linewidth = 0.5))) +
  scale_x_log10(breaks = c(2, 5, 10, 20, 40, 80), labels = function(x) paste0(virgola(x, 0), " km")) +
  scale_y_continuous(labels = function(y) virgola(y, 0, "%")) +
  labs(subtitle = paste0("A. Più lontani dal capoluogo e più grandi si è, meno si esce\n",
                         "le curve sono l'atteso del modello a due taglie fissate"),
       x = "distanza dal capoluogo di provincia (scala logaritmica)",
       y = "quota che esce dal comune per lavoro, 2021")

# --- B: il percentile, prima e dopo ---------------------------------------------------
# Due istogrammi impilati: sopra il grezzo, sotto il residuo. È lo stesso comune, la stessa
# misura, e la posizione cambia di dodici punti di percentile.
confronto <- bind_rows(
  transmute(comuni, valore = quota_fuori, pannello = "quota grezza"),
  transmute(comuni, valore = residuo, pannello = "residuo del modello\n(a parità di distanza e taglia)"))
righe_bagheria <- tibble::tibble(
  pannello = unique(confronto$pannello),
  valore = c(bagheria$quota_fuori, bagheria$residuo),
  percentile = c(percentile_grezzo, percentile_residuo))
mediane <- summarise(confronto, mediana = median(valore), .by = pannello)

posizione <- ggplot(confronto, aes(valore)) +
  geom_histogram(bins = 34, fill = "grey80", colour = "white", linewidth = 0.2) +
  geom_vline(data = mediane, aes(xintercept = mediana), colour = "grey35", linewidth = 0.5) +
  geom_vline(data = righe_bagheria, aes(xintercept = valore),
             colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 1) +
  geom_text(data = righe_bagheria, aes(x = valore, y = 36,
                                       label = paste0("Bagheria\n", virgola(percentile, 0, "° percentile"))),
            hjust = -0.1, vjust = 1, size = 3.1, fontface = "bold", lineheight = 1.05,
            colour = COLORI_TERRITORIO[["Bagheria"]]) +
  facet_wrap(~pannello, ncol = 1, scales = "free_x") +
  scale_x_continuous(labels = function(x) virgola(x, 0)) +
  labs(subtitle = paste0("B. La stessa Bagheria, prima e dopo il controllo\n",
                         "dal ", virgola(percentile_grezzo, 0, "°"), " al ",
                         virgola(percentile_residuo, 0, "° percentile"), ": l'anomalia era la taglia"),
       x = "quota che esce dal comune (%) e residuo (punti percentuali)", y = "comuni") +
  theme(panel.grid.major.x = element_blank())

figura <- (nuvola | posizione) +
  plot_layout(widths = c(1.25, 1)) +
  plot_annotation(
    title = "Bagheria si muove quanto un comune della sua taglia a quella distanza",
    subtitle = sommario(paste0(
      "Quota di pendolari che esce dal comune per lavoro, in percentuale dei pendolari del comune, messa in relazione con la distanza dal capoluogo di provincia: ",
      "il pannello A mostra tutti i comuni non capoluogo e le curve del valore atteso, il pannello B la posizione di Bagheria prima e dopo il controllo. ",
      "La figura serve a togliere di mezzo un claim, non a stabilirne uno: dice che «Bagheria si muove poco» è una lettura sbagliata di un numero giusto.\n",
      "Il dato grezzo mette Bagheria al ", virgola(percentile_grezzo, 0, "° percentile"),
      " dei 381 comuni siciliani non capoluogo per quota di chi esce a lavorare.\n",
      "Sembra un'anomalia, e i vicini la rafforzano: ", CONTRASTO$nome, " manda fuori il ",
      virgola(CONTRASTO$quota_fuori, 0, "%"), " dei suoi pendolari, Bagheria il ",
      virgola(bagheria$quota_fuori, 0, "%"), ".\n",
      "Ma fuori comune si va per mancanza di lavoro dentro, e Bagheria è il comune più grande della corona: ",
      migliaia(round(bagheria$pendolari)), " pendolari contro i ",
      migliaia(round(CONTRASTO$pendolari)), " di ", CONTRASTO$nome, ".\n",
      "Controllando distanza e dimensione, che sono due variabili geografiche e non di comportamento, il residuo è di ",
      virgola(bagheria$residuo, 1), " punti e il percentile sale al ",
      virgola(percentile_residuo, 0, "°"), ".\n",
      "La particolarità di Bagheria è chi si muove, e per quale motivo (figure 2 e 3)."), LARGHEZZA),
    caption = didascalia_2b(
      lettura = paste0(
        "nel pannello A ogni punto grigio è un comune e Bagheria è il punto vermiglio. Il diametro del punto è il numero di pendolari del comune, cioè proprio la variabile che spiega l'apparente anomalia: si vede a occhio che i comuni grandi stanno in basso. ",
        "L'asse orizzontale è logaritmico perché il modello è nel logaritmo della distanza: così il valore atteso appare come la retta che è. ",
        "Le due linee scure sono il valore atteso dal modello a due taglie fissate, e non una interpolazione dei punti: la distanza fra le due curve è quanto la sola taglia sposta l'atteso. ",
        "Nel pannello B ogni barra conta i comuni, e le due righe vermiglie sono Bagheria prima del controllo (quota grezza) e dopo (residuo del modello): il salto fra le due posizioni è il finding. ",
        "Il modello è una regressione lineare della quota di uscita sul logaritmo della distanza dal capoluogo e sul logaritmo del numero di pendolari (n = 381, R quadro = 0,31, errori standard HC3): serve a togliere di mezzo taglia e posizione, ",
        "e sono due regressori geografici senza nessuna pretesa causale. ",
        "La distanza è in linea d'aria fra i centroidi ISTAT (EPSG:32633): non è distanza stradale né tempo di viaggio, e per i comuni montani la sottostima. ",
        "I nove capoluoghi restano fuori perché per loro la misura non è definita: è l'unica esclusione dai 381 comuni disegnati."),
      fonte = paste0(
        "ISTAT, Matrice del pendolarismo, censimento permanente 2021, motivo lavoro, origine-destinazione comune per comune (conteggio esaustivo, non stima campionaria). ",
        "Elaborazione: notebooks/mobilita.ipynb (data/processed/mob_taglia_distanza.csv e mob_curva_attesa.csv)."),
      larghezza = LARGHEZZA),
    theme = tema_figura())

salva(figura, "mob_fig04_taglia_distanza", larghezza = LARGHEZZA, altezza = 23)
