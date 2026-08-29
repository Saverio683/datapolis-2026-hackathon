# Figura 7 — dove si perde chi: il profilo di ritenzione per età singola 2021-2024.
# I ragazzi escono a ondate (17-19 e 23-24) e in parte rientrano dopo i 26; le ragazze
# tengono fino ai 23 e da lì cedono senza rientri. La finestra utile per un intervento
# è 22-25 anni.
#
# La domanda gemella — *da quando* si perde, sulla scala decennale — sta in fig07b.
# Erano due pannelli della stessa figura, tenuti insieme da una "e" nel titolo: due
# domande, due fonti (età singole del permanente contro classi quinquennali di tre
# censimenti), due orizzonti temporali. Separate, ciascuna ha un titolo che è una frase
# sola e una caption che parla solo dei suoi dati.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Il vicinato entra come territorio unico, non come cinque linee: le coorti dei cinque
# comuni sono sommate prima del rapporto (nel notebook), così il denominatore è dello
# stesso ordine di Bagheria. Per età singola le curve dei singoli comuni oscillano di
# dieci punti e coprivano il grafico senza dire niente: chi vuole il dettaglio per comune
# lo trova in genere_ritenzione_eta_vicini.csv (la fig01, su un'altra misura, li tiene separati).
vicini <- vicini_di_bagheria()
vicinato <- read_csv(file.path(PROCESSED, "genere_ritenzione_eta_vicini.csv"),
                     col_types = cols(territorio = "c", nome_territorio = "c",
                                      genere = "c", .default = "d")) |>
  filter(territorio == "VICINI5")
ETICHETTA_VICINATO <- unique(vicinato$nome_territorio)
stopifnot(length(ETICHETTA_VICINATO) == 1)

COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))
SPESSORI <- c(Bagheria = 1.2, Palermo = 0.55, Sicilia = 0.55, Italia = 0.55,
              setNames(0.9, ETICHETTA_VICINATO))

dati <- bind_rows(
    read_csv(file.path(PROCESSED, "genere_ritenzione_eta.csv"), show_col_types = FALSE),
    vicinato
  ) |>
  filter(!is.na(ritenzione_rolling3_pct)) |>
  mutate(nome_territorio = factor(nome_territorio, levels = names(COLORI)),
         genere = factor(ETICHETTE_GENERE[genere], levels = ETICHETTE_GENERE))

# Serve al sottotitolo: la finestra 22-25 sulle ragazze, Bagheria contro il vicinato.
ritenzione <- function(territorio, eta) {
  dati$ritenzione_rolling3_pct[dati$nome_territorio == territorio &
                                 dati$genere == "femmine" & dati$eta_2021 == eta]
}

# La finestra 22-25 riguarda le ragazze: il rettangolo compare solo su quel pannello.
finestra <- tibble(genere = factor("femmine", levels = ETICHETTE_GENERE),
                   x0 = 22, x1 = 25)
note <- tibble(
  genere = factor(c("femmine", "maschi"), levels = ETICHETTE_GENERE),
  x = c(23.5, 30), y = c(105.3, 105.3), hjust = c(0.5, 1),
  testo = c("finestra utile: 22-25 anni", "rientri netti dopo i 26")
)

figura <- ggplot(dati, aes(eta_2021, ritenzione_rolling3_pct, colour = nome_territorio)) +
  geom_rect(data = finestra, aes(xmin = x0, xmax = x1, ymin = -Inf, ymax = Inf),
            inherit.aes = FALSE, fill = COLORI_TERRITORIO[["Bagheria"]], alpha = 0.08) +
  geom_hline(yintercept = 100, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_line(aes(linewidth = nome_territorio)) +
  geom_text(data = note, aes(x, y, label = testo, hjust = hjust),
            inherit.aes = FALSE, size = 3.3, fontface = "bold", colour = "grey25") +
  facet_wrap(~genere) +
  # breaks esplicito: fissa l'ordine della legenda invece di lasciarlo ai livelli dedotti.
  scale_colour_manual(values = COLORI, breaks = names(COLORI)) +
  # Bagheria è il soggetto: linea piena; i benchmark sono contesto, più sottili;
  # il vicinato sta in mezzo, è il confronto nuovo.
  scale_linewidth_manual(values = SPESSORI, guide = "none") +
  scale_x_continuous(breaks = seq(14, 30, 2)) +
  scale_y_continuous(labels = function(x) virgola(x, 1, "%")) +
  coord_cartesian(ylim = c(96, 106)) +
  guides(colour = guide_legend(override.aes = list(linewidth = 1.1))) +
  labs(
    title = "La finestra per trattenere le ragazze di Bagheria\nè fra i 22 e i 25 anni",
    subtitle = paste0(
      "Quota della coorte ancora residente dopo tre anni: chi aveva 20 anni nel 2021 ne ha 23 nel 2024. Sotto il tratteggio la coorte si è ridotta.\n",
      "I ragazzi escono a ondate, a 17-19 e a 23-24 anni, e in parte rientrano dopo i 26. Le ragazze tengono fino ai 23 e da lì cedono\n",
      "(96,7-97,9 sulle età 25-29, contro ~103 dell'Italia), senza rientri. E non è il vicinato: fra 22 e 25 anni i cinque comuni vicini restano\n",
      "piatti (", virgola(ritenzione(ETICHETTA_VICINATO, 22), 1, "%"), " → ",
      virgola(ritenzione(ETICHETTA_VICINATO, 25), 1, "%"), "), Bagheria scende da ",
      virgola(ritenzione("Bagheria", 22), 1, "%"), " a ",
      virgola(ritenzione("Bagheria", 25), 1, "%"),
      ". È l'età in cui il vantaggio educativo dovrebbe convertirsi in lavoro."),
    x = "età nel 2021 (nel 2024: tre anni in più)",
    y = "% della coorte 2021",
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - età singole, 2021 e 2024. Conteggi comunali di ~250-340 persone per età,\n",
      "media mobile su tre età: si leggono i pattern, non i decimali. Misura netta: comprende chi arriva e include l'aggiustamento post-censuario delle stime.\n",
      "Tre anni non bastano a chiamarla fuga: la stessa domanda su scala decennale, che la data al 2011-2021, sta in fig07b.\n",
      "I controlli interni al solo permanente sulla stessa coorte a cinque anni (2018-2023 e 2019-2024) concentrano la perdita sulla transizione\n",
      "20-24 → 25-29 - femmine 92,8% e 93,3% a Bagheria contro ~102% in Italia - cioè esattamente dove questo profilo colloca la finestra.\n",
      "Vicinato = ", paste(vicini$nome_comune, collapse = ", "),
      " (i cinque comuni più vicini per distanza fra i centroidi): coorti sommate prima del\n",
      "rapporto, non media dei cinque rapporti, così il denominatore regge il confronto con Bagheria. Le serie per singolo comune, troppo piccole per\n",
      "essere lette per età, restano in genere_ritenzione_eta_vicini.csv.\n",
      "Palermo è il controfattuale dichiarato del disegno di valutazione (notebook, sezione «Trend paralleli»).\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_ritenzione_eta.csv, genere_ritenzione_eta_vicini.csv")) +
  tema_figura()

salva(figura, "fig07_ritenzione_eta", larghezza = 28, altezza = 17)
