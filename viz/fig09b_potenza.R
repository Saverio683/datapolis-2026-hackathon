# Figura 9b — la finestra di lettura del KPI: quanto deve essere grande un effetto perché
# la fonte lo distingua da come il dato si muove da solo. Due metri affiancati: il modello
# binomiale (ogni annata un campione indipendente) e la variabilità osservata nei comuni
# siciliani di taglia simile a Bagheria, senza interventi. Aggregare anni abbassa il primo,
# non il secondo: il +1,40 pp del KPI realistico resta sotto la soglia in ogni finestra.
#
# Era il terzo pannello della fig09. Sta in una figura sua perché risponde a una domanda
# diversa da quella: là si contano persone, qui la misurabilità.
# Tutti i numeri arrivano dal notebook: qui si dispongono, non si ricalcolano.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Il tasso di occupazione è il KPI primario della proposal e va letto per primo;
# facet_wrap altrimenti ordina in alfabetico e mette le casalinghe in cima.
ORDINE_KPI <- c("tasso di occupazione F 15-24", "quota casalinghe F 15-24")

LARGHEZZA <- 24   # stessa misura del salvataggio: su questa il testo va a capo

base <- read_csv(file.path(PROCESSED, "genere_base_persone.csv"), show_col_types = FALSE)
mde <- read_csv(file.path(PROCESSED, "genere_mde.csv"), show_col_types = FALSE)
anno <- base$anno[1]

# Rilevabile = MDE osservata all'80% di potenza non più grande del delta che il KPI promette.
soglie <- mde |>
  rename(kpi = KPI, delta_pp = `delta da rilevare (pp)`, anni = `anni pooled per lato`,
         mde_bin = `MDE binomiale 80% (pp)`, mde_oss = `MDE osservata 80% (pp)`,
         pot_bin = `potenza binomiale (%)`, pot_oss = `potenza osservata (%)`,
         n_simili = `comuni simili`) |>
  mutate(
    rilevabile = mde_oss <= abs(delta_pp),
    finestra = factor(paste0(anni, ifelse(anni == 1, " anno", " anni")),
                      levels = paste0(3:1, ifelse(3:1 == 1, " anno", " anni"))),
    kpi = factor(sub(" \\(obiettivo: Palermo\\)", "", kpi), levels = ORDINE_KPI),
    etichetta = paste0("potenza ", virgola(pot_oss, 0, "%"), " (binomiale ",
                       virgola(pot_bin, 0, "%"), ")"),
    x_etichetta = pmax(mde_bin, mde_oss))
stopifnot(!anyNA(soglie$kpi), n_distinct(soglie$n_simili) == 1)
N_SIMILI <- soglie$n_simili[1]

riferimenti <- distinct(soglie, kpi, delta_pp)
prima_soglia <- filter(riferimenti, kpi == ORDINE_KPI[1])

occ <- filter(soglie, kpi == ORDINE_KPI[1])
cas <- filter(soglie, kpi == ORDINE_KPI[2])
di <- function(tab, colonna, n) tab[[colonna]][tab$anni == n]
DELTA_OCC <- abs(prima_soglia$delta_pp[1])
DELTA_CAS <- abs(cas$delta_pp[1])
# Sono i claim del titolo: sull'occupazione nessuna finestra vede il delta, sulle casalinghe
# lo vede il biennio. Se cambiassero, il titolo va riscritto.
stopifnot(!any(occ$rilevabile), di(cas, "rilevabile", 2))

figura <- ggplot(soglie, aes(y = finestra)) +
  facet_wrap(~kpi, ncol = 1, scales = "free_y") +
  geom_vline(data = riferimenti, aes(xintercept = abs(delta_pp)),
             colour = "grey45", linewidth = 0.4, linetype = "dashed") +
  geom_segment(aes(x = mde_bin, xend = mde_oss, yend = finestra),
               colour = "grey70", linewidth = 0.8) +
  geom_point(aes(x = mde_bin), shape = 21, size = 3.6, stroke = 1, fill = "white",
             colour = "grey45") +
  geom_point(aes(x = mde_oss, colour = rilevabile), size = 4.2) +
  geom_text(aes(x = x_etichetta, label = etichetta),
            hjust = -0.12, size = 3.2, fontface = "bold", colour = "grey20") +
  geom_text(data = prima_soglia, aes(x = abs(delta_pp), y = 3.95, label = "delta da rilevare"),
            hjust = -0.08, vjust = 0.5, size = 3.1, colour = "grey45") +
  scale_colour_manual(values = c(`TRUE` = "#0072B2", `FALSE` = "#9C9C9C"),
                      breaks = c(TRUE, FALSE),
                      labels = c(`TRUE` = "la finestra vede l'effetto promesso",
                                 `FALSE` = "l'effetto promesso resta sotto la soglia")) +
  scale_x_continuous(limits = c(0, 4.4), breaks = 0:4, expand = expansion(mult = c(0, 0.02))) +
  scale_y_discrete(expand = expansion(add = c(0.85, 1.5))) +
  coord_cartesian(clip = "off") +
  guides(colour = guide_legend(override.aes = list(size = 4.2))) +
  labs(
    title = "Aggregare anni non basta: sull'occupazione\nnessuna finestra vede l'effetto promesso",
    subtitle = sommario(paste0(
      "Differenza minima rilevabile all'80% di potenza (MDE, in punti percentuali) per i due indicatori di popolazione della proposta, secondo quanti anni si accorpano in ciascun lato del confronto. ",
      "Pallino vuoto: modello binomiale, che tratta ogni annata come un campione indipendente. Pallino pieno: variabilità osservata, senza interventi, nei ",
      N_SIMILI, " comuni siciliani di taglia simile a Bagheria. È una figura di disegno della misura, non un risultato sui giovani.\n",
      "Sull'occupazione femminile il binomiale promette che tre anni per lato bastino (potenza ", virgola(di(occ, "pot_bin", 3), 0),
      "%); nei comuni simili la soglia resta fra ", virgola(min(occ$mde_oss), 2), " e ", virgola(max(occ$mde_oss), 2),
      " punti in ogni finestra, sopra il delta di ", virgola(DELTA_OCC, 2), ", e la potenza sul triennio è del ",
      virgola(di(occ, "pot_oss", 3), 0), "%. ",
      "Sulle casalinghe (delta ", virgola(DELTA_CAS, 1), " punti) passa solo il biennio, con potenza ",
      virgola(di(cas, "pot_oss", 2), 0), "%.\n",
      "Per questo il tasso comunale si legge come direzione della convergenza, e l'effetto del servizio si misura sui partecipanti."), LARGHEZZA),
    x = "punti percentuali", y = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "ogni riga è una finestra di lettura: «anni pooled» è l'ampiezza di ciascuno dei due lati del confronto, quindi tre anni sono un triennio contro un triennio. ",
        "Il pallino vuoto è la soglia binomiale (potenza 80%, alfa 5% bilaterale, trasformazione arcoseno); il pallino pieno è 2,8 volte la deviazione standard delle variazioni dei comuni simili, al netto della variazione mediana del gruppo. ",
        "Il tratto grigio unisce i due metri della stessa finestra. La riga tratteggiata verticale è il delta che il KPI promette (l'allineamento a Palermo di fig09). ",
        "Il colore è la conclusione sul metro osservato: blu quando la soglia sta a sinistra del tratteggio, grigio quando lo supera. Accanto a ogni riga la potenza sul delta promesso, osservata e fra parentesi binomiale. ",
        "Comuni simili: fra metà e il doppio delle ragazze 15-24 di Bagheria nel ", anno, ", Bagheria esclusa. ",
        "Il metro osservato contiene anche le divergenze reali fra comuni e non contiene la variabilità propria di Palermo. ",
        "Il triennio che i dati permettono (2018, 2019 e 2021 contro 2022-2024) attraversa la rottura di misura del 2021; il biennio 2021-2022 contro 2023-2024 no. ",
        "Un pallino grigio non significa che l'intervento non funzioni, ma che quella lettura non basterebbe a dimostrarlo."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, 390 comuni siciliani, 2018-2024 (manca il 2020). ",
        "Numerosità di base di Bagheria: ", migliaia(base$popolazione_F_15_24[1]), " ragazze di 15-24 anni nel ", anno, ". ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_mde.csv e genere_base_persone.csv)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig09b_potenza", larghezza = LARGHEZZA, altezza = 20)
