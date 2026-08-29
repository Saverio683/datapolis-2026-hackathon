# Figura 9b — la finestra di lettura del KPI: quanto deve essere grande un effetto perché
# una rilevazione lo veda. Il +1,40 pp del KPI realistico (fig09) non si distingue da zero
# su una lettura annuale; si distingue su un triennio pooled.
#
# Era il terzo pannello della fig09. Sta in una figura sua perché risponde a una domanda
# diversa da quella: là si contano persone, qui potenza statistica. Accorpate, il titolo
# doveva reggere due affermazioni separate da una virgola, e la caption spiegava insieme
# l'arrotondamento dei quadratini e la trasformazione arcoseno.
# Tutti i numeri arrivano dal notebook: qui si dispongono, non si ricalcolano.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Il tasso di occupazione è il KPI primario della proposal e va letto per primo;
# facet_wrap altrimenti ordina in alfabetico e mette le casalinghe in cima.
ORDINE_KPI <- c("tasso di occupazione F 15-24", "quota casalinghe F 15-24")

base <- read_csv(file.path(PROCESSED, "genere_base_persone.csv"), show_col_types = FALSE)
mde <- read_csv(file.path(PROCESSED, "genere_mde.csv"), show_col_types = FALSE)
anno <- base$anno[1]

# Rilevabile = MDE all'80% di potenza non più grande del delta che il KPI promette.
soglie <- mde |>
  rename(kpi = KPI, delta_pp = `delta da rilevare (pp)`, anni = `anni pooled per lato`,
         mde_pp = `MDE 80% (pp)`, potenza = `potenza per il delta (%)`) |>
  mutate(
    rilevabile = mde_pp <= abs(delta_pp),
    finestra = factor(paste0(anni, ifelse(anni == 1, " anno", " anni")),
                      levels = paste0(3:1, ifelse(3:1 == 1, " anno", " anni"))),
    kpi = factor(sub(" \\(obiettivo: Palermo\\)", "", kpi), levels = ORDINE_KPI))
stopifnot(!anyNA(soglie$kpi))

riferimenti <- distinct(soglie, kpi, delta_pp)
# L'etichetta della soglia si scrive una volta sola, nel primo pannello: ripeterla
# raddoppierebbe il testo senza aggiungere niente.
prima_soglia <- filter(riferimenti, kpi == ORDINE_KPI[1])

# I numeri del sottotitolo si leggono dal dato: il KPI primario su un anno solo e su tre.
primario <- filter(soglie, kpi == ORDINE_KPI[1])
soglia_di <- function(n) primario$mde_pp[primario$anni == n]
potenza_di <- function(n) primario$potenza[primario$anni == n]
DELTA <- abs(prima_soglia$delta_pp[1])
# È il claim del titolo: un anno non basta, tre sì. Se cambiasse, la frase va riscritta.
stopifnot(!primario$rilevabile[primario$anni == 1], primario$rilevabile[primario$anni == 3])

figura <- ggplot(soglie, aes(mde_pp, finestra)) +
  facet_wrap(~kpi, ncol = 1, scales = "free_y") +
  geom_vline(data = riferimenti, aes(xintercept = abs(delta_pp)),
             colour = "grey45", linewidth = 0.4, linetype = "dashed") +
  geom_segment(aes(x = 0, xend = mde_pp, yend = finestra, colour = rilevabile),
               linewidth = 2.4, lineend = "round") +
  geom_point(aes(colour = rilevabile), size = 4.2) +
  geom_text(aes(label = paste0("potenza ", virgola(potenza, 0, "%"))),
            hjust = -0.35, size = 3.3, fontface = "bold", colour = "grey20") +
  # L'annotazione della soglia sopra la prima riga, non alla sua altezza: lì incrociava
  # l'etichetta della potenza del primo anno.
  geom_text(data = prima_soglia, aes(x = abs(delta_pp), y = 3.95, label = "delta da rilevare"),
            hjust = -0.08, vjust = 0.5, size = 3.1, colour = "grey45") +
  scale_colour_manual(values = c(`TRUE` = "#0072B2", `FALSE` = "#9C9C9C"),
                      breaks = c(TRUE, FALSE),
                      labels = c(`TRUE` = "la finestra vede l'effetto promesso",
                                 `FALSE` = "l'effetto promesso resta sotto la soglia")) +
  scale_x_continuous(limits = c(0, 3.9), expand = expansion(mult = c(0, 0.02))) +
  # Le tre finestre stavano troppo vicine perché le etichette della potenza non si
  # toccassero: qui l'aria è sopra e sotto la pila, non fra le barre.
  scale_y_discrete(expand = expansion(add = c(0.85, 1.5))) +
  coord_cartesian(clip = "off") +
  guides(colour = guide_legend(override.aes = list(linewidth = 0, size = 4.2))) +
  labs(
    title = "Un anno di rilevazione non distingue da zero l'effetto\nche il KPI promette; un triennio sì",
    subtitle = paste0(
      "Il pallino è la differenza minima rilevabile (MDE) all'80% di potenza: sotto quella soglia un effetto c'è ma la lettura non lo vede.\n",
      "Il tratteggio è il delta che il KPI promette (+", virgola(DELTA, 2),
      " punti, l'allineamento a Palermo di fig09). Su un anno solo la soglia sta\n",
      "a ", virgola(soglia_di(1), 2), " punti, oltre il doppio del promesso: la potenza è ",
      virgola(potenza_di(1), 0), "%, poco più di un lancio di moneta. Su tre anni pooled\n",
      "la soglia scende a ", virgola(soglia_di(3), 2), " punti e la potenza sale al ",
      virgola(potenza_di(3), 0), "%.\n",
      "Per questo i KPI primari si leggono su trienni pooled (2022-2024 contro 2025-2027), e l'anno per anno spetta a indicatori\n",
      "di processo — utenza per età e genere — che oggi nessuno rileva."),
    x = "punti percentuali", y = NULL,
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - condizione professionale, classe 15-24 anni, ", anno, ".\n",
      "MDE = differenza minima rilevabile a potenza 80% e alfa 5% fra due proporzioni (trasformazione arcoseno); \"anni pooled\" = ampiezza di ciascuno dei due lati del confronto.\n",
      "La soglia dipende dalla numerosità, che a Bagheria è di ~2.900 ragazze per annata: è un limite della rilevazione, non una debolezza dell'intervento.\n",
      "Il delta da rilevare è quello della fig09, dove lo stesso obiettivo è tradotto in persone e messo di fronte al restringimento della platea.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_mde.csv, genere_base_persone.csv")) +
  tema_figura()

salva(figura, "fig09b_potenza", larghezza = 24, altezza = 16)
