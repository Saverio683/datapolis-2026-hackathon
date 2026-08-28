# Figura 8 — la terza lente di confronto: i gruppi di pari, al plurale.
# Le altre figure confrontano Bagheria con la gerarchia amministrativa (Palermo, Sicilia,
# Italia) e con il vicinato geografico. Qui il confronto è con i comuni che le somigliano,
# e la domanda è quale conclusione sopravvive al cambio di definizione di "somigliare":
#   - pari STRUTTURALI (questo thread): dimensione, densità, età, stranieri, abitazioni,
#     distanza da Palermo — variabili che non sono esiti;
#   - pari per ISTRUZIONE (thread educazione): caliper di popolazione sull'isola e
#     distanza che include il profilo educativo, esclude gli esiti.
# I due gruppi condividono un solo comune, quindi la seconda colonna è un test vero.
# Sei indicatori su otto danno lo stesso giudizio con entrambe: quelli si possono
# affermare. Gli altri due dipendono da chi si sceglie come pari, e la figura lo mostra
# invece di scegliere la lente più comoda.
# `verso` (quale direzione è "meglio") arriva dal notebook: è una scelta interpretativa e
# non va rifatta qui. Il colore la usa, la posizione mostra il dato grezzo.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

posizionamento <- read_csv(file.path(PROCESSED, "genere_posizionamento.csv"),
                           show_col_types = FALSE)

# Chi sta in quale gruppo: la figura conta l'overlap, non lo ricopia.
lenti <- read_csv(file.path(PROCESSED, "genere_pari_lenti.csv"), show_col_types = FALSE)
condivisi <- filter(lenti, lente == "entrambe")

# Il modello del thread educazione sullo stesso indicatore L14: quanto Bagheria sta sotto
# il valore atteso dai suoi tratti territoriali. Serve al sottotitolo, con le sue cautele:
# il CV R² dice che il modello spiega quasi nulla, quindi è un segno, non una quantità.
modello <- read_csv(file.path(PROCESSED, "edu_model_robustness_2011.csv"),
                    show_col_types = FALSE) |>
  filter(outcome == "L14", modello == "C_contesto_territoriale")
stopifnot(nrow(modello) == 1)

# Nomi corti per l'asse: quelli per esteso stanno nella colonna `nome` del CSV.
BREVI <- c(L11 = "occupazione femminile 15+",
           L7  = "disoccupazione femminile 15+",
           I1  = "differenziale educativo M/F",
           L4  = "NEET 15-29",
           L14 = "occupazione giovanile 15-29",
           F4  = "giovani che vivono da soli",
           F7  = "coppie giovani con figli",
           M2  = "mobilità fuori comune")
stopifnot(setequal(names(BREVI), posizionamento$indicatore))

N_GEMELLE <- posizionamento$n_gemelle[1]
N_ISTRUITI <- posizionamento$n_istruiti[1]
N_REGIONE <- posizionamento$n_regione[1]
stopifnot(N_GEMELLE == N_ISTRUITI)   # stessa scala per i due pannelli dei pari
MEDIANA_PARI <- N_GEMELLE / 2

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
    # Dentro ciascun gruppo: "estrema" = fuori dall'intervallo interquartile del gruppo.
    giudizio_gemelle = giudica(verso, bagheria >= gemelle_q1 & bagheria <= gemelle_q3,
                               bagheria > gemelle_q3),
    giudizio_istruiti = giudica(verso, bagheria >= istruiti_q1 & bagheria <= istruiti_q3,
                                bagheria > istruiti_q3),
    # Nella regione: stessa idea, sui quartili della distribuzione dei 390.
    giudizio_regione = giudica(verso, percentile_390 >= 25 & percentile_390 <= 75,
                               percentile_390 > 50),
    concorde = giudizio_gemelle == giudizio_istruiti,
    # L'ordine delle righe lo fissa la prima lente: così, se le due leggessero allo stesso
    # modo, anche il secondo pannello scenderebbe monotono. Non lo fa, e la rottura della
    # monotonia È il finding — non serve nessun marcatore in più per vederla.
    breve = factor(breve, levels = rev(breve[order(gemelle_sotto)])))

# I numeri che il titolo e il sottotitolo citano si leggono qui, dal dato: se il
# posizionamento cambia, la figura non può continuare a raccontare la versione vecchia.
conta <- function(ind, chiave) dati[[paste0(chiave, "_sotto")]][dati$indicatore == ind]
CONCORDI <- sum(dati$concorde)
# Il titolo scrive "sei su otto" a parole: l'assert è ciò che impedisce alla frase di
# sopravvivere a un dato che non la sostiene più.
stopifnot(CONCORDI == 6, nrow(dati) == 8,
          setequal(dati$indicatore[!dati$concorde], c("L11", "I1")))

# La legenda dice cosa significano i tre colori: prima stava nel sottotitolo, che è il
# posto sbagliato per una chiave di lettura — si legge una volta e poi non si ritrova più
# mentre si guarda il grafico. `limits` fissa le tre voci anche se una classe non comparisse
# nel dato, così la chiave è sempre completa.
ETICHETTE_GIUDIZIO <- c(peggio = "Bagheria sta peggio del riferimento",
                        neutro = "nella norma, o indicatore senza verso \"buono\" (*)",
                        meglio = "Bagheria sta meglio del riferimento")

#' Un pannello "dentro un gruppo di pari": identico nei due casi tranne il gruppo letto,
#' così la differenza fra i due è solo nel dato e mai nella grammatica del disegno.
#' `chiave` è il prefisso delle colonne nel CSV; `legenda` accende la scala solo nel primo
#' pannello, perché patchwork la raccoglie una volta sola.
pannello_pari <- function(chiave, sottotitolo, legenda) {
  sotto <- dati[[paste0(chiave, "_sotto")]]
  ggplot(dati, aes(sotto, breve, colour = .data[[paste0("giudizio_", chiave)]])) +
    geom_vline(xintercept = MEDIANA_PARI, colour = "grey80", linewidth = 0.4) +
    geom_segment(aes(x = MEDIANA_PARI, xend = sotto, yend = breve),
                 linewidth = 2.4, lineend = "round") +
    geom_point(size = 4.6) +
    geom_text(aes(label = paste0(sotto, "/", N_GEMELLE)),
              nudge_x = ifelse(sotto >= MEDIANA_PARI, 0.7, -0.7),
              size = 3.3, fontface = "bold", colour = "grey20") +
    (if (legenda) {
      list(scale_colour_manual(values = DIVERGENTE, limits = names(DIVERGENTE),
                               labels = ETICHETTE_GIUDIZIO, name = NULL),
           guides(colour = guide_legend(override.aes = list(size = 4.6))))
     } else scale_colour_manual(values = DIVERGENTE, guide = "none")) +
    # Il limite sinistro tiene conto dell'etichetta, non solo del punto: a 0/10 il
    # testo sta fuori dal pallino e a -1.1 veniva tagliato dal bordo del pannello.
    scale_x_continuous(limits = c(-1.9, N_GEMELLE + 1.4), breaks = seq(0, N_GEMELLE, 2),
                       expand = expansion(mult = 0)) +
    labs(subtitle = sottotitolo,
         # I due pannelli dei pari sono adiacenti e condividono la scala: il titolo
         # dell'asse si scrive sotto il primo, ripeterlo sotto il secondo è rumore.
         x = if (legenda) paste0("comuni sotto Bagheria (", MEDIANA_PARI,
                                 " = mediana del gruppo)") else NULL,
         y = NULL)
}

# --- pannelli A e B: le due definizioni di "comune simile" ---------------------------
strutturali <- pannello_pari(
  "gemelle",
  paste0("Fra i pari strutturali\nquante delle ", N_GEMELLE,
         " gemelle stanno sotto Bagheria"),
  legenda = TRUE)

istruiti <- pannello_pari(
  "istruiti",
  paste0("E fra i pari per istruzione\nstesso conteggio, altri ", N_ISTRUITI, " comuni"),
  legenda = FALSE) +
  theme(axis.text.y = element_blank())

# --- pannello C: la posizione nella regione ------------------------------------------
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
  labs(subtitle = paste0("E dentro tutta la regione\n",
                         "percentile sui ", N_REGIONE, " comuni siciliani"),
       x = "percentile (50 = mediana regionale)", y = NULL) +
  theme(axis.text.y = element_blank())

# La legenda in una riga tutta sua, in cima (come in fig07): come prima riga della
# composizione `guide_area()` finisce sopra i titoli dei pannelli invece che incastrata
# fra i titoli e i grafici.
figura <- guide_area() /
  ((strutturali | istruiti | regione) + plot_layout(widths = c(1.34, 1, 1.06))) +
  plot_layout(heights = c(0.07, 1), guides = "collect") +
  plot_annotation(
    title = "Sei indicatori su otto non dipendono da quali pari si scelgono; l'occupazione femminile sì",
    subtitle = paste0(
      "Due gruppi di comuni simili a Bagheria, costruiti su variabili diverse e con un solo comune in comune (", condivisi$nome_comune[1],
      "): quello che sopravvive a entrambi si può affermare.\n",
      "Reggono a tutte e due le letture i tre tratti che contano per la proposal: la disoccupazione femminile alta (", conta("L7", "gemelle"), "/", N_GEMELLE,
      " in entrambi), l'occupazione giovanile bassa (", conta("L14", "gemelle"), "/", N_GEMELLE, "),\n",
      "e soprattutto i giovani che vivono da soli — nessun comune, di nessuno dei due gruppi, ne ha meno. Quella è l'autonomia mancata, ed è il tratto proprio di Bagheria.\n",
      "Cambia invece proprio il claim centrale del thread: sull'occupazione femminile fra i pari strutturali Bagheria è nella norma (", conta("L11", "gemelle"), "/", N_GEMELLE,
      ", dentro i quartili),\n",
      "fra i comuni ugualmente scolarizzati è penultima (", conta("L11", "istruiti"), "/", N_GEMELLE, ", sotto il primo quartile). Non è uno svantaggio di fascia: a pari istruzione, il lavoro femminile non arriva.\n",
      "Concorde il modello del thread educazione: sull'occupazione giovanile Bagheria sta ", virgola(abs(modello$residuo_bagheria), 1),
      " punti sotto il valore atteso dai suoi tratti territoriali — un segno, non una misura (vedi caption)."),
    caption = paste0(
      "Fonte: ISTAT, 8milaCensus, censimento 2011.\n",
      "Fasce diverse per indicatore: 15+ (occupazione e disoccupazione F), 6+ (differenziale educativo), 15-29 (NEET, occupazione giovanile), totale famiglie (giovani soli, coppie con figli), residenti (mobilità).\n",
      "Pari strutturali = i ", N_GEMELLE, " comuni più simili per dimensione, densità, età, stranieri, abitazioni e distanza da Palermo (matching Mahalanobis su variabili non-esito; robustezza 8/", N_GEMELLE, " e 6/", N_GEMELLE, " sugli altri metodi).\n",
      "Pari per istruzione = i ", N_ISTRUITI, " comuni appaiati dal thread educazione con un disegno indipendente: caliper di popolazione 0,5-2x su tutta l'isola e distanza che include il profilo educativo (I5, I6, I7) ed esclude gli esiti.\n",
      "Che i due gruppi condividano un solo comune non è un difetto di nessuno dei due: rispondono a domande diverse (\"strutturalmente simile\" e \"ugualmente scolarizzato\") e non vanno mai fusi in una classifica sola.\n",
      "Che il differenziale educativo M/F cambi lettura fra i due pannelli è atteso e non è un finding: il secondo gruppo è appaiato anche sull'istruzione, quindi su quell'asse è simile per costruzione.\n",
      "Il verso è fissato nel notebook: alto è meglio per occupazione femminile, occupazione giovanile e giovani soli, peggio per disoccupazione, NEET e differenziale educativo M/F. (*) F7 e M2 restano descrittivi.\n",
      "Il colore compare solo fuori dalla metà centrale del riferimento: oltre i quartili del gruppo nei due pannelli dei pari, sotto il 25° o sopra il 75° percentile regionale nel terzo. Il pallino mostra sempre la posizione, anche quando è grigio.\n",
      "Il residuo del modello (occupazione 15-29 osservata meno prevista dai tratti territoriali) vale ", virgola(modello$residuo_bagheria, 1), " punti [bootstrap 95%: ", virgola(modello$residuo_ci95_basso, 1), "; ", virgola(modello$residuo_ci95_alto, 1),
      "], ma il modello ha un R2 in validazione incrociata di ", virgola(modello$r2_cv_10fold, 2), ": spiega quasi nulla.\n",
      "Va letto come conferma di segno insieme agli altri due pannelli, mai come effetto attribuibile al comune, e in nessun caso come nesso causale.\n",
      "Anno e fascia diversi dalle serie 15-24 del thread: è il gruppo di controllo storico, mai un termine di paragone con il censimento permanente 2018-2024.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_posizionamento.csv, genere_pari_lenti.csv; pipeline/edu - data/processed/edu_model_robustness_2011.csv"),
    theme = tema_figura()
  )

salva(figura, "fig08_posizionamento", larghezza = 32, altezza = 18)
