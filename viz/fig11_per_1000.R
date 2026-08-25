# Figura 11 — istruzione e lavoro sulla stessa fascia, su base 1.000.
# L'estrazione sta nel notebook («Su 1.000 ragazze»): sotto i 15 anni un diploma è
# impossibile, quindi le diplomate 9-24 sono le diplomate 15-24; il denominatore viene
# dalle età singole. Le due quote poggiano così sulla STESSA popolazione — ma non sono
# incatenate: l'incrocio titolo × condizione non esiste a livello comunale, e chi lavora
# non è un sottoinsieme di chi ha il diploma. Barre parallele, mai stadi di un funnel.
# Il pannello destro legge l'attainment dove ha senso (18-24), come bound superiore.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

dati <- read_csv(file.path(PROCESSED, "genere_per_1000.csv"), show_col_types = FALSE)
anno_rif <- max(dati$anno)
dati <- filter(dati, anno == anno_rif)

ETICHETTA_VICINATO <- dati$nome_territorio[startsWith(dati$nome_territorio, "vicinato")][1]
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")
dati <- mutate(dati,
               nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)),
               genere_nome = factor(ETICHETTE_GENERE[genere], levels = ETICHETTE_GENERE))

v <- function(terr, gen, colonna) dati[[colonna]][dati$nome_territorio == terr & dati$genere == gen]

# --- pannello A: per 1.000 residenti 15-24, diploma e lavoro in parallelo ------------
# Due misure sulla stessa base, non due identità: grigio per il diploma (contesto),
# vermiglio per il lavoro (il punto della figura è la conversione mancata).
MISURE <- c(per_1000_diploma = "con almeno il diploma", per_1000_occupati = "al lavoro")
COLORI_MISURA <- setNames(c("#9C9C9C", "#D55E00"), MISURE)

lungo <- dati |>
  pivot_longer(all_of(names(MISURE)), names_to = "misura", values_to = "per_1000") |>
  mutate(misura = factor(MISURE[misura], levels = MISURE))

parallele <- ggplot(lungo, aes(per_1000, nome_territorio, fill = misura)) +
  facet_wrap(~genere_nome) +
  geom_col(position = position_dodge(width = 0.72), width = 0.6) +
  geom_text(aes(label = per_1000), position = position_dodge(width = 0.72),
            hjust = -0.22, size = 3.2, fontface = "bold", colour = "grey20") +
  scale_fill_manual(values = COLORI_MISURA, name = NULL) +
  scale_x_continuous(limits = c(0, 640), breaks = seq(0, 600, 200),
                     expand = expansion(mult = c(0, 0.02))) +
  labs(subtitle = paste0("Su 1.000 residenti 15-24, quante/i…\n",
                         "stessa popolazione per le due quote, ", anno_rif),
       x = paste0("per 1.000 residenti 15-24 (", anno_rif, ")"), y = NULL)

# --- pannello B: attainment 18-24, dove il diploma è raggiungibile -------------------
attainment <- ggplot(dati, aes(`almeno_diploma_18_24_bound_%`, nome_territorio)) +
  geom_line(aes(group = nome_territorio), colour = "grey75", linewidth = 1.8,
            lineend = "round") +
  geom_point(aes(colour = genere), size = 4.2) +
  geom_text(aes(label = virgola(`almeno_diploma_18_24_bound_%`, 0),
                hjust = ifelse(genere == "F", -0.45, 1.45), colour = genere),
            size = 3.2, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE, name = NULL) +
  scale_x_continuous(limits = c(58, 82), breaks = seq(60, 80, 10),
                     labels = \(x) virgola(x, 0, "%")) +
  labs(subtitle = "Quota con almeno il diploma a 18-24 anni\nbound superiore, stessa fonte",
       x = "% con almeno il diploma, 18-24 anni", y = NULL) +
  theme(axis.text.y = element_blank())

figura <- (parallele | attainment) +
  plot_layout(widths = c(1.75, 1)) +
  plot_annotation(
    title = "Il diploma le ragazze lo raggiungono più dei ragazzi; il lavoro, la metà",
    subtitle = paste0(
      "Su 1.000 ragazze 15-24 di Bagheria (", anno_rif, "): ", v("Bagheria", "F", "per_1000_diploma"),
      " hanno almeno il diploma e ", v("Bagheria", "F", "per_1000_occupati"),
      " lavorano. Su 1.000 coetanei: ", v("Bagheria", "M", "per_1000_diploma"),
      " e ", v("Bagheria", "M", "per_1000_occupati"), ".\n",
      "Le due quote vivono sulla stessa popolazione — il conteggio dei diplomi 9-24 è per costruzione quello 15-24, nessuno ha un diploma prima —\n",
      "ma non sono stadi di un funnel: quante delle diplomate lavorino il censimento comunale non lo dice, e chi lavora può non avere il diploma.\n",
      "A destra la fascia in cui il diploma è raggiungibile: il vantaggio femminile resta (+",
      virgola(v("Bagheria", "F", "almeno_diploma_18_24_bound_%") - v("Bagheria", "M", "almeno_diploma_18_24_bound_%")),
      " pp) ma il primato del 9-24 no — Sicilia e Italia stanno sopra.\n",
      "Ciò che distingue Bagheria a ogni fascia è il distacco dal vicinato, e una conversione in lavoro che il diploma non muove."),
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - istruzione (9-24), condizione professionale (15-24), demografia per età singola (2021-2024), anno ", anno_rif, ".\n",
      "Estrazione: diplomate/i 15-24 = diplomate/i 9-24 (nessun titolo sotto i 15 anni, esatto per costruzione); denominatori dalle età singole; coerenza fra le tavole verificata nel notebook (scarto zero).\n",
      "Il 18-24 è un bound superiore: qualche qualifica IFP si ottiene a 17 anni (stessa logica dei bounds sulle casalinghe). L'incrocio titolo × condizione non è pubblicato a livello comunale.\n",
      "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media dei cinque valori.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_per_1000.csv"),
    theme = tema_datapolis()
  )

salva(figura, "fig11_per_1000", larghezza = 28, altezza = 15)
