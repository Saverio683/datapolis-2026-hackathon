# Figura 6 — il piano istruzione × occupazione per i quattro territori di confronto:
# la freccia va dal punto maschile a quello femminile, e punta ovunque in basso a destra
# (più istruite, meno occupate). A Bagheria arriva più in basso di tutte.
#
# Era il pannello sinistro di una figura che ne teneva due. L'altro — la stessa relazione
# sui 390 comuni siciliani al 2011 — è stato prima scorporato in fig06b e poi ritirato: su
# 390 punti il rho valeva -0,24, cioè una nuvola senza pendenza visibile, e il grafico non
# reggeva il titolo che gli stava sopra. Con quattro territori la relazione si vede, e resta
# qui. La fig06b adesso mostra un'altra cosa: dove sta Bagheria dentro la distribuzione
# siciliana dell'occupazione femminile, annata per annata.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

quadrante <- read_csv(file.path(PROCESSED, "genere_quadrante.csv"), show_col_types = FALSE)
anno <- unique(quadrante$anno)

largo <- quadrante |>
  pivot_wider(id_cols = c(territorio, nome_territorio),
              names_from = genere, values_from = c(tasso_occupazione, `almeno_diploma_%`))
etichette <- largo |>
  mutate(nudge_x = c(0, 0, 0.25, 0.25), nudge_y = c(-1.1, 1.1, -1.1, 1.1))  # ordine del csv

# I numeri del titolo e del sottotitolo si leggono dal dato: se cambia, la frase non può
# continuare a raccontare la versione vecchia.
bag <- filter(largo, nome_territorio == "Bagheria")
divari <- largo$`almeno_diploma_%_F` - largo$`almeno_diploma_%_M`
DIVARIO_BAG <- divari[largo$nome_territorio == "Bagheria"]
# La freccia punta in basso a destra ovunque e Bagheria è l'estremo su entrambe le scale:
# è il claim del titolo, e le tre righe sono ciò che impedisce alla frase di sopravvivere
# a un dato che non la sostiene più.
stopifnot(all(largo$`almeno_diploma_%_F` > largo$`almeno_diploma_%_M`),
          all(largo$tasso_occupazione_F < largo$tasso_occupazione_M),
          DIVARIO_BAG == max(divari),
          bag$tasso_occupazione_F == min(largo$tasso_occupazione_F))

figura <- ggplot(largo) +
  geom_segment(aes(x = `almeno_diploma_%_M`, y = tasso_occupazione_M,
                   xend = `almeno_diploma_%_F`, yend = tasso_occupazione_F),
               colour = "grey65", linewidth = 0.7,
               arrow = arrow(length = unit(2.6, "mm"), type = "closed")) +
  geom_point(data = quadrante,
             aes(`almeno_diploma_%`, tasso_occupazione, colour = genere), size = 3.4) +
  geom_text(data = etichette,
            aes(`almeno_diploma_%_F` + nudge_x, tasso_occupazione_F + nudge_y,
                label = nome_territorio),
            size = 3.5, fontface = "bold", colour = "grey25") +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  labs(
    title = "La freccia punta in basso a destra in tutti e quattro i territori,\ne a Bagheria arriva più in basso di tutte",
    subtitle = paste0(
      "Ogni freccia va dal punto maschile a quello femminile: verso destra le ragazze sono più istruite dei coetanei, verso il basso\n",
      "sono meno occupate. Nessuno dei quattro territori fa eccezione al verso — a distinguere Bagheria è quanto in basso arriva:\n",
      "sul 9-24 il vantaggio nel diploma è il più ampio del panel (+", virgola(DIVARIO_BAG, 1),
      " punti) e il tasso di occupazione femminile è il più basso (", virgola(bag$tasso_occupazione_F, 1), "%)."),
    x = "quota con almeno il diploma, 9-24 anni (%)",
    y = "tasso di occupazione 15-24 anni (%)",
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - istruzione (9-24 anni), condizione professionale (15-24 anni), anno ", anno, ".\n",
      "Le due fasce non coincidono ma vivono sulla stessa popolazione: nessuno consegue un titolo prima dei 15 anni, quindi i diplomati 9-24 sono i diplomati 15-24.\n",
      "Il contesto regionale - dove cade Bagheria nella distribuzione dei 390 comuni siciliani per occupazione femminile - sta in fig06b:\n",
      "fascia e anni diversi, mai da leggere in serie con questa.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_quadrante.csv")) +
  tema_figura()

salva(figura, "fig06_quadrante", larghezza = 22, altezza = 16)
