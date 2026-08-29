# Figura edu-09 (appendice A) — i modelli di sensibilità, e quanto valgono.
# Claim del thread educazione (invariato): il residuo occupazionale di Bagheria è negativo
# in tutte e tre le specifiche, MA la capacità predittiva fuori campione per l'occupazione
# è debole e per il NEET storico è moderata. Per questo i modelli restano in appendice e
# non quantificano l'impatto della policy. Bagheria è esclusa dall'addestramento; analisi
# ecologica, mai causale.
#
# PERCHÉ QUESTA FORMA E NON DUE PANNELLI DI RESIDUI (figures/edu/12).
# Tre difetti, e il terzo è quello che conta.
#   1. I due pannelli avevano l'asse verticale ORIENTATO AL CONTRARIO: sull'occupazione
#      "peggio dell'atteso" era in basso, sul NEET in alto. Due pannelli affiancati che
#      dicono la stessa cosa con due grammatiche opposte costringono a ribaltare la
#      lettura a metà figura. Qui il residuo è in punti favorevoli e tutti e sei stanno
#      dalla stessa parte dello zero, che è anche il modo in cui il claim li enuncia.
#   2. Il colore separava i due esiti, ma i due esiti concordano: la tinta suggeriva un
#      contrasto che nel dato non c'è.
#   3. Il R² in validazione incrociata — cioè il motivo per cui questa pagina è in
#      appendice — era testo grigio di otto punti sotto ai pallini. La cautela più
#      importante dell'intera analisi non aveva peso visivo. Qui ha un pannello suo, e
#      soprattutto torna dentro il pannello dei residui: i modelli che non prevedono
#      niente hanno il pallino VUOTO. Il numero si vede e insieme si vede che non si usa.
#
# Colore: nessuna scala per l'esito. Vermiglio perché il soggetto è Bagheria; la
# distinzione che conta — affidabile o no — passa dal riempimento, non dalla tinta,
# perché è una cautela e deve leggersi anche in bianco e nero.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 28

modelli <- read_csv(file.path(PROCESSED, "edu_model_robustness_2011.csv"),
                    show_col_types = FALSE)

# Il verso degli esiti arriva dalla pipeline, come in ogni altra figura del thread: sul
# NEET salire è peggio, sull'occupazione è meglio, e da lì dipende il segno del residuo
# "favorevole". Non si ricopia a mano.
versi <- read_csv(file.path(PROCESSED, "edu_historical_bagheria.csv"),
                  show_col_types = FALSE) |>
  distinct(indicatore, direzione)

ESITI <- c(L14 = "Occupazione giovanile 15-29", L4 = "NEET 15-29")
SPECIFICHE <- c(A_istruzione = "A · solo istruzione",
                B_istruzione_mobilita = "B · istruzione + mobilità",
                C_contesto_territoriale = "C · contesto territoriale")

stopifnot(setequal(modelli$outcome, names(ESITI)),
          setequal(modelli$modello, names(SPECIFICHE)))

dati <- modelli |>
  inner_join(versi, by = c("outcome" = "indicatore")) |>
  mutate(
    alto_favorevole = direzione == "alto = favorevole",
    # Residuo in punti FAVOREVOLI. Sul NEET il residuo grezzo è positivo e significa
    # "Bagheria sta peggio dell'atteso": ribaltarlo mette tutti e sei i punti dalla stessa
    # parte dello zero, che è quello che il claim afferma. Gli estremi dell'intervallo si
    # ribaltano e si SCAMBIANO, altrimenti il basso finisce sopra l'alto.
    residuo = ifelse(alto_favorevole, residuo_bagheria, -residuo_bagheria),
    ci_basso = ifelse(alto_favorevole, residuo_ci95_basso, -residuo_ci95_alto),
    ci_alto = ifelse(alto_favorevole, residuo_ci95_alto, -residuo_ci95_basso),
    # Un R² in validazione incrociata sotto zero non è "poca capacità predittiva": è un
    # modello che sbaglia PIÙ di quanto sbaglierebbe rispondendo sempre la media. Sotto
    # quella soglia il residuo non è una quantità da citare, e il pallino resta vuoto.
    affidabile = r2_cv_10fold > 0,
    esito = factor(ESITI[outcome], levels = ESITI),
    specifica = factor(SPECIFICHE[modello], levels = rev(SPECIFICHE)))

stopifnot(nrow(dati) == length(ESITI) * length(SPECIFICHE),
          all(dati$ci_basso <= dati$residuo), all(dati$residuo <= dati$ci_alto))

# Il claim in due controlli: tutti i residui sfavorevoli, e sull'occupazione nessuna
# specifica arriva a una capacità predittiva utile. Se la pipeline cambiasse, la figura
# si ferma invece di raccontare la versione vecchia.
stopifnot(all(dati$residuo < 0), all(dati$ci_alto < 0))
N_INAFFIDABILI <- sum(!dati$affidabile)
r2_occupazione <- dati$r2_cv_10fold[dati$outcome == "L14"]
r2_neet <- dati$r2_cv_10fold[dati$outcome == "L4"]
stopifnot(max(r2_occupazione) < 0.1, min(r2_neet) > 0.3)

# L'etichetta del pannello destro sta a sinistra del pallino pieno perché il R² in
# validazione è sempre il più basso dei due: è la definizione di sovradattamento, e se
# smettesse di valere l'etichetta finirebbe sopra il segmento.
stopifnot(all(dati$r2_cv_10fold < dati$r2_in_sample))

N_TRAINING <- unique(dati$n_comuni_training)
stopifnot(length(N_TRAINING) == 1)

ETICHETTE_FIDUCIA <- c(`TRUE` = "il modello prevede meglio della media",
                       `FALSE` = "il modello prevede PEGGIO della media: residuo non citabile")
RIEMPIMENTO <- c(`TRUE` = COLORI_TERRITORIO[["Bagheria"]], `FALSE` = "white")

# --- pannello A: quanto Bagheria sta sotto il valore atteso ---------------------------
residui <- ggplot(dati, aes(residuo, specifica)) +
  facet_wrap(~esito, ncol = 1, scales = "free_y") +
  geom_vline(xintercept = 0, linewidth = 0.6, colour = "grey30") +
  geom_linerange(aes(xmin = ci_basso, xmax = ci_alto), linewidth = 1.1,
                 colour = COLORI_TERRITORIO[["Bagheria"]]) +
  geom_point(aes(fill = as.character(affidabile)), size = 4.6, shape = 21, stroke = 1.3,
             colour = COLORI_TERRITORIO[["Bagheria"]]) +
  # All'estremo sinistro dell'intervallo, non sopra il pallino: le tre righe di un
  # pannello sono vicine e l'etichetta "sopra" finiva sulla barra della riga accanto.
  # Fuori dall'estremo non c'è nient'altro da coprire.
  geom_text(aes(x = ci_basso, label = virgola(residuo, 1, taglia_zero = FALSE)),
            hjust = 1, nudge_x = -0.28, size = 3.2, fontface = "bold",
            colour = "grey20") +
  scale_fill_manual(values = RIEMPIMENTO, labels = ETICHETTE_FIDUCIA,
                    limits = names(RIEMPIMENTO), name = NULL) +
  guides(fill = guide_legend(override.aes = list(size = 4.6), ncol = 1)) +
  scale_x_continuous(limits = c(-9.4, 0.6), breaks = seq(-8, 0, 2),
                     labels = function(x) virgola(x, 0), expand = expansion(mult = 0)) +
  scale_y_discrete(expand = expansion(add = c(0.6, 0.85))) +
  labs(subtitle = paste0("Quanto Bagheria sta sotto il valore atteso\n",
                         "residuo in punti favorevoli, con intervallo bootstrap 95%"),
       x = "osservato − previsto, in punti favorevoli", y = NULL)

# --- pannello B: quanto il modello sa prevedere davvero -------------------------------
# Il salto dal R² in campione a quello in validazione incrociata è la misura di quanto il
# modello stia imparando il rumore. Come dumbbell il salto è una lunghezza; come due
# numeri in una tabella non lo vede nessuno.
capacita <- ggplot(dati, aes(y = specifica)) +
  facet_wrap(~esito, ncol = 1, scales = "free_y") +
  # Sotto lo zero il modello è peggio di una costante. La banda lo dice una volta per
  # tutte, invece di lasciarlo dedurre dal segno di un numero piccolo.
  annotate("rect", xmin = -Inf, xmax = 0, ymin = -Inf, ymax = Inf, fill = "grey93") +
  geom_vline(xintercept = 0, linewidth = 0.6, colour = "grey30") +
  geom_segment(aes(x = r2_in_sample, xend = r2_cv_10fold), linewidth = 2.2,
               colour = "grey80", lineend = "round") +
  geom_point(aes(x = r2_in_sample), size = 3.4, shape = 21, stroke = 1.1,
             fill = "white", colour = "grey55") +
  geom_point(aes(x = r2_cv_10fold, fill = as.character(affidabile)), size = 4.6,
             shape = 21, stroke = 1.3, colour = COLORI_TERRITORIO[["Bagheria"]]) +
  geom_text(aes(x = r2_cv_10fold, label = virgola(r2_cv_10fold, 2, taglia_zero = FALSE)),
            hjust = 1, nudge_x = -0.022, size = 3.2, fontface = "bold",
            colour = "grey20") +
  scale_fill_manual(values = RIEMPIMENTO, guide = "none") +
  scale_x_continuous(limits = c(-0.21, 0.62), breaks = seq(0, 0.6, 0.2),
                     labels = function(x) virgola(x, 1), expand = expansion(mult = 0)) +
  scale_y_discrete(expand = expansion(add = c(0.6, 0.85))) +
  labs(subtitle = paste0("E quanto quel numero vale\n",
                         "R² in campione (vuoto) → in validazione incrociata (pieno)"),
       x = "R² (sotto zero il modello prevede peggio della media)", y = NULL) +
  theme(axis.text.y = element_blank())

figura <- (residui | capacita) +
  plot_layout(widths = c(1.16, 1), guides = "collect") +
  plot_annotation(
    title = paste0("Bagheria sta sotto l'atteso in tutte e ", nrow(dati),
                   " le specifiche; sull'occupazione nessuna delle tre sa prevedere niente"),
    subtitle = sommario(paste0(
      "Due esiti del censimento 2011, tre modelli ciascuno, addestrati sugli altri ",
      N_TRAINING, " comuni siciliani con Bagheria esclusa. A sinistra: tutti e sei i residui sono sfavorevoli e nessun intervallo tocca lo zero.\n",
      "A destra il motivo per cui questa resta una pagina d'appendice. Sull'occupazione il R² in validazione vale ",
      paste(virgola(sort(r2_occupazione), 2, taglia_zero = FALSE), collapse = ", "),
      ": ", N_INAFFIDABILI, " di quei tre modelli prevedono peggio di chi rispondesse sempre la media (sono quelli col pallino vuoto) e il terzo, a ",
      virgola(max(r2_occupazione), 2, taglia_zero = FALSE),
      ", non fa molto meglio. Su quell'esito il residuo ha un segno leggibile e nessuna grandezza citabile.\n",
      "Sul NEET storico la capacità predittiva è moderata (",
      virgola(min(r2_neet), 2, taglia_zero = FALSE), "-", virgola(max(r2_neet), 2, taglia_zero = FALSE),
      "), e lì il residuo si legge come misura, restando descrittivo."), LARGHEZZA),
    caption = didascalia_4b(
      mostra = paste0(
        "quanto Bagheria si discosta dal valore che un modello, addestrato sugli altri comuni siciliani, le assegnerebbe. ",
        "A sinistra il residuo (osservato meno previsto) su due esiti del censimento 2011 e tre specifiche ciascuno; a destra la capacità predittiva di ognuno di quei modelli. ",
        "I due pannelli vanno letti insieme: il primo dice il segno dello scarto, il secondo dice se quel numero abbia una grandezza citabile."),
      base = paste0(
        "N = ", N_TRAINING, " comuni siciliani nell'addestramento, con Bagheria sempre esclusa: il valore previsto è quello che gli altri comuni le assegnerebbero senza averla mai vista. ",
        "Intervalli di confidenza bootstrap al 95% sul residuo; capacità predittiva misurata come R quadro in validazione incrociata a 10 falde, cioè su dati mai visti in addestramento. ",
        "Sono regressioni ecologiche fra comuni e mai causali: il residuo dice che Bagheria si discosta dai comuni con tratti simili, non che un tratto produca l'esito, e non stima l'effetto di una politica né quello del titolo di studio su una persona. ",
        "Il residuo è in punti favorevoli, cioè osservato meno previsto dove salire è meglio (occupazione) e il segno opposto dove salire è peggio (NEET); gli estremi dell'intervallo si ribaltano e si scambiano insieme al residuo, così il basso resta il basso. ",
        "L'R quadro in validazione incrociata può essere negativo, e su alcuni modelli qui lo è: significa che sui dati non visti il modello sbaglia più di una costante pari alla media. Non è un R quadro «piccolo», è un modello senza contenuto predittivo, e nessun numero che ne esce va riportato come quantità. ",
        "Le tre specifiche aggiungono variabili una sull'altra (istruzione, poi mobilità, poi contesto territoriale) e non sono modelli alternativi da mettere in gara: servono a vedere se il segno del residuo sopravvive a specifiche diverse, che è l'unica domanda a cui questa pagina risponde."),
      lettura = paste0(
        "nel pannello di sinistra ogni riga è una specifica e la barra orizzontale è l'intervallo di confidenza al 95% del residuo: che nessun intervallo tocchi lo zero significa che lo scarto è nella stessa direzione in tutte le specifiche. ",
        "Nel pannello di destra il pallino pieno segnala un modello con capacità predittiva positiva, il pallino vuoto un modello che sui dati non visti fa peggio della semplice media: davanti a un pallino vuoto il residuo della riga corrispondente si legge solo come segno, mai come misura. ",
        "La riga verticale allo zero separa i due casi."),
      fonte = paste0(
        "ISTAT, 8milaCensus, censimento 2011. ",
        "Elaborazione: pipeline/edu (thread educazione), data/processed/edu_model_robustness_2011.csv e edu_historical_bagheria.csv."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "edu_fig09_appendice_modelli", larghezza = LARGHEZZA, altezza = 25)
