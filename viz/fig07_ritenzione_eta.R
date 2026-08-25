# Figura 7 — quando si perde chi, e da quando.
# Sopra: il profilo di ritenzione per età singola 2021-2024. I ragazzi escono a ondate
# (17-19 e 23-24) e in parte rientrano dopo i 26; le ragazze tengono fino ai 23 e da lì
# cedono senza rientri. La finestra utile per un intervento è 22-25 anni.
# Sotto: la stessa domanda su scala decennale, dalle classi quinquennali. Serve a
# rispondere all'obiezione ovvia — tre anni di dati non bastano a chiamare "fuga" una
# perdita. Nel decennio 2001-2011 Bagheria *guadagnava* coorti; nel 2011-2021 ne perde
# più di Palermo. La frattura è databile, ed è lo stesso decennio del muro di fig10.

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

profilo <- ggplot(dati, aes(eta_2021, ritenzione_rolling3_pct, colour = nome_territorio)) +
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
  labs(subtitle = paste("Dove si perde chi — profilo per età singola, 2021-2024",
                        "(chi aveva 20 anni nel 2021 ne ha 23 nel 2024; media mobile su 3 età)"),
       x = "età nel 2021 (nel 2024: tre anni in più)",
       y = "% della coorte 2021")

# --- pannello inferiore: da quando -----------------------------------------------------
# Stessa coorte (chi ha 15-19 anni all'inizio) seguita per dieci anni, due volte. Le
# classi quinquennali permettono solo passi di cinque anni: il decennio è due classi
# avanti, ed è la scala più corta che copra sia il 2001-2011 sia il 2011-2021.
decennale <- read_csv(file.path(PROCESSED, "genere_ritenzione_decennale.csv"),
                      col_types = cols(territorio = "c", nome_territorio = "c",
                                       genere = "c", eta_da = "c", eta_a = "c",
                                       fonti_diverse = "c", .default = "d"))
COORTE <- "Y15-19"
decenni <- decennale |>
  filter(anni == 10, eta_da == COORTE) |>
  mutate(periodo = paste0(anno_da, "-", anno_a),
         nome_territorio = factor(nome_territorio, levels = names(COLORI)),
         genere = factor(ETICHETTE_GENERE[genere], levels = ETICHETTE_GENERE))

bagheria_decenni <- filter(decenni, nome_territorio == "Bagheria")
salto <- bagheria_decenni |>
  summarise(scarto = ritenzione_pct[anno_da == max(anno_da)] -
              ritenzione_pct[anno_da == min(anno_da)], .by = genere)
scarto_di <- function(g) abs(salto$scarto[salto$genere == g])

quando <- ggplot(decenni, aes(periodo, ritenzione_pct, colour = nome_territorio,
                              group = nome_territorio)) +
  geom_hline(yintercept = 100, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_line(aes(linewidth = nome_territorio)) +
  geom_point(size = 2.4) +
  # Solo Bagheria porta i valori: è il soggetto, e con quattro etichette per estremo il
  # pannello diventa illeggibile (nel 2011-2021 tre territori stanno in tre punti).
  geom_text(data = bagheria_decenni,
            aes(label = virgola(ritenzione_pct, 1, "%"),
                vjust = if_else(anno_da == min(anno_da), -1.2, 2.0)),
            size = 3.2, fontface = "bold", show.legend = FALSE) +
  geom_text(data = salto, inherit.aes = FALSE,
            aes(x = 1.5, y = 82, label = paste0(virgola(scarto), " punti in un decennio")),
            size = 3.2, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]]) +
  facet_wrap(~genere) +
  # guide "none" qui: le due legende (linee sopra, linee+punti sotto) hanno chiavi diverse
  # e patchwork non le fonde, ne stampa due. Quella buona è la superiore, che ha anche il
  # vicinato; il pannello inferiore usa gli stessi colori e non ne aggiunge una seconda.
  scale_colour_manual(values = COLORI, breaks = names(COLORI), guide = "none") +
  scale_linewidth_manual(values = SPESSORI, guide = "none") +
  scale_x_discrete(expand = expansion(add = c(0.35, 0.45))) +
  scale_y_continuous(labels = function(x) virgola(x, 0, "%")) +
  coord_cartesian(ylim = c(78, 118)) +
  labs(subtitle = paste("Da quando — la stessa coorte (15-19 anni all'inizio) seguita per dieci anni;",
                        "tratteggio a 100 = la coorte si conserva"),
       x = NULL, y = "coorte dopo dieci anni")

figura <- profilo / quando +
  plot_layout(heights = c(1.3, 1), guides = "collect") +
  plot_annotation(
    title = "La finestra per trattenere le ragazze è fra i 22 e i 25 anni, e la falla si è aperta nel decennio 2011-2021",
    subtitle = paste0(
      "In alto: i ragazzi di Bagheria escono a ondate, a 17-19 e a 23-24 anni, e in parte rientrano dopo i 26; le ragazze tengono fino ai 23 e da lì\n",
      "cedono (96,7-97,9 sulle età 25-29, contro ~103 dell'Italia), senza rientri. E non è il vicinato: fra 22 e 25 anni i cinque comuni vicini restano\n",
      "piatti (", virgola(ritenzione(ETICHETTA_VICINATO, 22), 1, "%"), " → ",
      virgola(ritenzione(ETICHETTA_VICINATO, 25), 1, "%"), "), Bagheria scende da ",
      virgola(ritenzione("Bagheria", 22), 1, "%"), " a ",
      virgola(ritenzione("Bagheria", 25), 1, "%"), ".\n",
      "In basso: tre anni di dati non basterebbero a chiamarla fuga, dieci sì. Nel decennio 2001-2011 Bagheria tratteneva la coorte meglio di Sicilia\n",
      "e Palermo; nel decennio successivo ne perde ", virgola(scarto_di("femmine")),
      " punti sulle ragazze e ", virgola(scarto_di("maschi")),
      " sui ragazzi, arrivando sotto Palermo sui maschi.\n",
      "La perdita è databile e non è finita: i controlli a cinque anni dentro il solo censimento permanente la ritrovano sulla transizione 20-24 → 25-29,\n",
      "cioè esattamente dove il profilo qui sopra colloca la finestra."),
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione. Pannello superiore: età singole, 2021 e 2024 - conteggi comunali di ~250-340 persone per età,\n",
      "media mobile su tre età, si leggono i pattern non i decimali. Misura netta: comprende chi arriva e include l'aggiustamento post-censuario delle stime.\n",
      "Pannello inferiore: classi quinquennali dei censimenti 2001 e 2011 e del censimento permanente 2021 (DF_DCSS_POP_DEMCITMIG_TV_1 le serve tutte e tre).\n",
      "Il decennio 2011-2021 ha una gamba per rilevazione: il 2011 è decennale, il 2021 permanente. La distorsione nota va nel verso prudente - il censimento 2011\n",
      "contò meno dell'anagrafe, quindi sta al denominatore del decennio che crolla e al numeratore di quello che tiene: il divario fra i due decenni è una stima per difetto.\n",
      "Controlli interni al solo permanente sulla stessa coorte a cinque anni (2018-2023 e 2019-2024): la perdita si concentra sulla transizione 20-24 → 25-29,\n",
      "femmine 92,8% e 93,3% a Bagheria contro ~102% in Italia. Tutti i periodi stanno in data/processed/genere_ritenzione_decennale.csv.\n",
      "Palermo è il controfattuale dichiarato del disegno di valutazione (notebook, sezione «Trend paralleli»).\n",
      "Vicinato = ", paste(vicini$nome_comune, collapse = ", "),
      " (i cinque comuni più vicini per distanza fra i centroidi): coorti sommate prima\n",
      "del rapporto, non media dei cinque rapporti, così il denominatore regge il confronto con Bagheria. Le serie per singolo comune, troppo piccole per essere\n",
      "lette per età, restano in genere_ritenzione_eta_vicini.csv. Il vicinato non compare nel pannello inferiore: le classi quinquennali sono state scaricate\n",
      "solo per i quattro territori di confronto.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_ritenzione_eta.csv, genere_ritenzione_eta_vicini.csv, genere_ritenzione_decennale.csv"),
    theme = tema_datapolis()
  )

salva(figura, "fig07_ritenzione_eta", larghezza = 28, altezza = 26)
