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

# Una costante sola: il testo va a capo sulla stessa larghezza con cui la figura viene
# salvata. Tenerle separate è il modo sicuro di scoprire un testo tagliato guardando il PNG.
LARGHEZZA <- 28

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

# Numeri della didascalia, tutti letti dai dati disegnati: nessuna cifra scritta a mano.
# La coorte di partenza è quella del 2021, cioè il denominatore del rapporto.
base_bagheria <- dati |> filter(nome_territorio == "Bagheria")
N_F <- sum(base_bagheria$n_2021[base_bagheria$genere == "femmine"])
N_M <- sum(base_bagheria$n_2021[base_bagheria$genere == "maschi"])
N_ETA_MIN <- min(base_bagheria$n_2021)
N_ETA_MAX <- max(base_bagheria$n_2021)
ETA_MIN <- min(dati$eta_2021)
ETA_MAX <- max(dati$eta_2021)

# La coda femminile dopo la finestra: il livello a cui Bagheria si assesta, contro l'Italia.
coda <- function(territorio) {
  v <- dati$ritenzione_rolling3_pct[dati$nome_territorio == territorio &
                                      dati$genere == "femmine" &
                                      dati$eta_2021 >= 25 & dati$eta_2021 <= 29]
  c(min = min(v), max = max(v), media = mean(v))
}
CODA_BAG <- coda("Bagheria")
CODA_ITA <- coda("Italia")
CODA_SIC <- coda("Sicilia")

# Il controllo di robustezza dentro la sola rilevazione permanente: la stessa coorte
# seguita per cinque anni, due volte. Sta in un file, quindi si legge e non si ricopia.
decennale <- read_csv(file.path(PROCESSED, "genere_ritenzione_decennale.csv"),
                      show_col_types = FALSE)
cinque_anni <- function(terr) {
  r <- decennale[decennale$nome_territorio == terr & decennale$anni == 5 &
                   decennale$eta_da == "Y20-24" & decennale$genere == "F" &
                   decennale$anno_da %in% c(2018, 2019), ]
  r <- r[order(r$anno_da), ]
  list(periodi = paste0(r$anno_da, "-", r$anno_a, collapse = " e "),
       valori = paste(virgola(r$ritenzione_pct, 1, "%"), collapse = " e "),
       media = mean(r$ritenzione_pct))
}
CTRL_BAG <- cinque_anni("Bagheria")
CTRL_ITA <- cinque_anni("Italia")

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
    subtitle = sommario(paste0(
      "Residenti di ogni età nel 2024 per 100 residenti della stessa coorte nel 2021: chi aveva 20 anni nel 2021 ne ha 23 nel 2024. ",
      "Per età singola da ", ETA_MIN, " a ", ETA_MAX, " anni, per genere, su cinque territori. È una misura netta di saldo, che comprende sia chi parte sia chi arriva: ",
      "dice a che età si perde, non da quando, e la stessa domanda su scala decennale sta in fig07b. Sotto il tratteggio la coorte si è ridotta.\n",
      "I ragazzi escono a ondate, a 17-19 e a 23-24 anni, e in parte rientrano dopo i 26. Le ragazze tengono fino ai 23 e da lì cedono, ",
      "senza rientri: sulle età 25-29 restano fra ", virgola(CODA_BAG[["min"]], 1, "%"), " e ",
      virgola(CODA_BAG[["max"]], 1, "%"), ", contro una media di ",
      virgola(CODA_SIC[["media"]], 1, "%"), " in Sicilia e di ", virgola(CODA_ITA[["media"]], 1, "%"),
      " in Italia, che cresce per immigrazione.\n",
      "Ed è un tratto di Bagheria: fra i 22 e i 25 anni i cinque comuni vicini restano piatti (",
      virgola(ritenzione(ETICHETTA_VICINATO, 22), 1, "%"), " e ",
      virgola(ritenzione(ETICHETTA_VICINATO, 25), 1, "%"), "), mentre Bagheria scende da ",
      virgola(ritenzione("Bagheria", 22), 1, "%"), " a ",
      virgola(ritenzione("Bagheria", 25), 1, "%"),
      ". È l'età in cui il vantaggio educativo dovrebbe convertirsi in lavoro."), LARGHEZZA),
    x = "età nel 2021 (nel 2024: tre anni in più)",
    y = "% della coorte del 2021",
    caption = didascalia_2b(
      lettura = paste0(
        "la riga tratteggiata orizzontale a 100% è la parità: sopra la coorte è cresciuta, sotto si è ridotta. ",
        "Il rettangolo vermiglio chiaro, presente solo sul pannello delle femmine, è la finestra 22-25 anni, misurata sull'età del 2021: chi aveva 22-25 anni nel 2021 ne ha 25-28 nel 2024, ed è in quei tre anni che la coorte si riduce. ",
        "Bagheria è in vermiglio e con la linea più spessa perché è il soggetto. ",
        "Le linee sono medie mobili centrate su tre età, quindi si leggono i pattern e non i decimali; le età ai bordi servono solo a chiudere la media mobile e restano fuori dal grafico. ",
        "Vicinato = ", paste(vicini$nome_comune, collapse = ", "),
        ", cioè i cinque comuni più vicini per distanza fra i centroidi: le coorti sono sommate prima del rapporto, non è la media dei cinque rapporti, così il denominatore regge il confronto con Bagheria. ",
        "Le serie dei singoli comuni, troppo piccole per essere lette per età, restano in genere_ritenzione_eta_vicini.csv. "),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, età singole, anni 2021 e 2024. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_ritenzione_eta.csv e genere_ritenzione_eta_vicini.csv)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig07_ritenzione_eta", larghezza = LARGHEZZA, altezza = 20)
