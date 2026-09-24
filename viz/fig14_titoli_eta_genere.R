# Figura 14 — il titolo di studio oltre la fascia 9-24, per genere e per territorio.
# Due domande in due pannelli. In alto: il vantaggio delle donne nei titoli regge nelle
# classi adulte e sul terziario? Sì fino a 49 anni, pari a 50-64, rovesciato sopra i 65.
# In basso: sui titoli degli adulti (25-49) Bagheria sta sopra o sotto i comuni vicini?
# A metà, e sotto Palermo, Sicilia e Italia.
# Il 25-49 non è la fascia target: è la classe in cui il percorso di studio è concluso,
# come in fig13b. Quante diplomate lavorino qui non si vede (fig11, fig13b).

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 28   # stessa misura del salvataggio: su questa il testo va a capo

dati <- read_csv(file.path(PROCESSED, "genere_titoli_eta.csv"),
                 col_types = cols(territorio = "c", eta = "c", genere = "c",
                                  nome_territorio = "c", ruolo = "c", .default = "d"))
anno_rif <- max(dati$anno)
dati <- filter(dati, anno == anno_rif)

MISURE <- c("almeno_diploma_%" = "Almeno il diploma", "terziario_%" = "Titolo terziario")
CLASSI <- c("Y9-24" = "9-24 anni", "Y25-49" = "25-49 anni", "Y50-64" = "50-64 anni",
            "Y_GE65" = "65 anni e più")
ETICHETTA_VICINATO <- unique(dati$nome_territorio[dati$ruolo == "vicinato"])
VICINI <- unique(dati$nome_territorio[dati$ruolo == "vicino"])

lungo <- dati |>
  pivot_longer(all_of(names(MISURE)), names_to = "misura", values_to = "quota") |>
  mutate(misura = factor(MISURE[misura], levels = MISURE))

q <- function(terr, classe, gen, mis) {
  lungo$quota[lungo$nome_territorio == terr & lungo$eta == classe & lungo$genere == gen &
                lungo$misura == MISURE[[mis]]]
}
gap <- function(terr, classe, mis) q(terr, classe, "F", mis) - q(terr, classe, "M", mis)

# I claim del titolo, letti dal dato: se cambiano, le frasi vanno riscritte.
quota_vicini <- sort(sapply(VICINI, q, classe = "Y25-49", gen = "T", mis = "almeno_diploma_%"),
                     decreasing = TRUE)
sopra <- names(quota_vicini)[quota_vicini > q("Bagheria", "Y25-49", "T", "almeno_diploma_%")]
sotto <- setdiff(names(quota_vicini), sopra)
# La cautela della didascalia: su quante persone poggiano i comuni che precedono Bagheria.
residenti_sopra <- migliaia(round(mean(dati$popolazione[dati$nome_territorio %in% sopra &
                                                         dati$eta == "Y25-49" & dati$genere == "T"]), -2))
stopifnot(gap("Bagheria", "Y25-49", "almeno_diploma_%") > 0,
          gap("Bagheria", "Y25-49", "terziario_%") > gap("Bagheria", "Y25-49", "almeno_diploma_%"),
          gap("Bagheria", "Y_GE65", "almeno_diploma_%") < 0,
          length(sopra) > 0, length(sotto) > 0,
          all(sapply(c("Palermo", "Sicilia", "Italia"), q, classe = "Y25-49", gen = "T",
                     mis = "almeno_diploma_%") > q("Bagheria", "Y25-49", "T", "almeno_diploma_%")))

LIMITI <- c(-7, 92)   # il margine sotto lo zero ospita le etichette dei valori piccoli
X_TOTALE <- 90   # la colonna dei valori totali del pannello in basso, a destra dei dati
asse_x <- scale_x_continuous(limits = LIMITI, breaks = seq(0, 80, 20),
                             labels = \(x) virgola(x, 0, "%"),
                             expand = expansion(mult = 0))
# Il titolo di ciascun pannello sta nella striscia dei riquadri e non in labs(subtitle):
# la legenda raccolta da patchwork si infilerebbe fra quel titolo e il suo grafico.
strisce <- function(prefisso) as_labeller(\(m) paste0(prefisso, ": ", tolower(m)))
scala_genere <- scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE, name = NULL)

# Etichetta all'esterno del segmento: il valore maggiore a destra, il minore a sinistra.
# Sopra i 65 anni il maggiore è quello maschile, quindi il lato non si decide dal genere.
esterne <- function(d) {
  d |>
    group_by(riga, misura) |>
    mutate(destra = quota == max(quota)) |>
    ungroup() |>
    mutate(hjust = if_else(destra, 0, 1), x_testo = quota + if_else(destra, 1.6, -1.6))
}

# --- pannello A: Bagheria per classe d'età ------------------------------------------------
pa <- lungo |>
  filter(nome_territorio == "Bagheria", genere %in% c("F", "M")) |>
  mutate(riga = factor(CLASSI[eta], levels = rev(CLASSI))) |>
  esterne()

pann_a <- ggplot(pa, aes(quota, riga)) +
  geom_line(aes(group = riga), colour = "grey75", linewidth = 1.8, lineend = "round") +
  geom_point(aes(colour = genere), size = 4.2) +
  geom_text(aes(x = x_testo, label = virgola(quota, 1, taglia_zero = FALSE), hjust = hjust, colour = genere),
            size = 3.1, fontface = "bold", show.legend = FALSE) +
  facet_wrap(~misura, nrow = 1, labeller = strisce("Bagheria, per classe d'età")) +
  asse_x + scala_genere +
  coord_cartesian(clip = "off") +
  guides(colour = "none") +
  labs(x = NULL, y = NULL)

# --- pannello B: 25-49 anni, Bagheria fra i vicini e i territori di confronto -------------
ordine_b <- dati |>
  filter(eta == "Y25-49", genere == "T") |>
  arrange(`almeno_diploma_%`) |>
  pull(nome_territorio)
pb <- lungo |>
  filter(eta == "Y25-49") |>
  mutate(riga = factor(nome_territorio, levels = ordine_b))
fila_bagheria <- which(ordine_b == "Bagheria")
pb_generi <- pb |> filter(genere %in% c("F", "M")) |> esterne()
pb_totale <- pb |> filter(genere == "T")

pann_b <- ggplot(pb_generi, aes(quota, riga)) +
  annotate("rect", xmin = -Inf, xmax = Inf, ymin = fila_bagheria - 0.48,
           ymax = fila_bagheria + 0.48, fill = "#FBE3D3") +
  geom_line(aes(group = riga), colour = "grey75", linewidth = 1.6, lineend = "round") +
  geom_point(aes(colour = genere), size = 3.6) +
  geom_point(data = pb_totale, aes(shape = "maschi e femmine insieme"), colour = "grey10",
             size = 4.6) +
  geom_text(data = filter(pb_generi, nome_territorio == "Bagheria"),
            aes(x = x_testo, label = virgola(quota, 1, taglia_zero = FALSE), hjust = hjust, colour = genere),
            size = 3.0, fontface = "bold", show.legend = FALSE) +
  geom_text(data = pb_totale, aes(x = X_TOTALE, label = virgola(quota, 1, taglia_zero = FALSE)), hjust = 1,
            size = 3.0, colour = "grey20",
            fontface = if_else(pb_totale$nome_territorio == "Bagheria", "bold", "plain")) +
  annotate("text", x = X_TOTALE, y = length(ordine_b) + 0.75, label = "insieme", hjust = 1,
           size = 2.7, colour = "grey40") +
  facet_wrap(~misura, nrow = 1, labeller = strisce("25-49 anni, tutti i territori")) +
  asse_x + scala_genere +
  scale_shape_manual(values = c("maschi e femmine insieme" = 124), name = NULL) +
  coord_cartesian(clip = "off") +
  guides(colour = guide_legend(order = 1), shape = guide_legend(order = 2)) +
  labs(x = "% dei residenti della stessa classe d'età e dello stesso genere", y = NULL)

# --- composizione ---------------------------------------------------------------------------
v <- function(terr, classe, gen, mis, d = 1) virgola(q(terr, classe, gen, mis), d, "%")
figura <- pann_a / pann_b +
  plot_layout(heights = c(4, 10), guides = "collect") +
  plot_annotation(
    title = paste0("Sotto i 50 anni le donne di Bagheria hanno più titoli degli uomini, soprattutto il terziario;\n",
                   "sul livello Bagheria sta a metà fra i comuni vicini e sotto la Sicilia"),
    subtitle = sommario(paste0(
      "Quota di residenti con almeno il diploma e con un titolo terziario (ITS, laurea di primo e di secondo livello, dottorato), ",
      "in percentuale dei residenti della stessa classe d'età e dello stesso genere, anno ", anno_rif, ". ",
      "In alto Bagheria sulle quattro classi d'età della tavola istruzione comunale; in basso la sola classe 25-49 su Bagheria, ",
      "i cinque comuni più vicini (uno per uno e insieme), Palermo, Sicilia e Italia. Il 25-49 non è la fascia target: è la classe in cui il percorso di studio è concluso. ",
      "La figura non dice quante diplomate lavorino: il lavoro per età e genere sta in fig13b.\n",
      "A 25-49 anni ha almeno il diploma il ", v("Bagheria", "Y25-49", "F", "almeno_diploma_%"),
      " delle donne contro il ", v("Bagheria", "Y25-49", "M", "almeno_diploma_%"),
      " degli uomini, e un titolo terziario il ", v("Bagheria", "Y25-49", "F", "terziario_%"),
      " contro il ", v("Bagheria", "Y25-49", "M", "terziario_%"),
      "; sopra i 65 anni sono avanti gli uomini (", v("Bagheria", "Y_GE65", "M", "almeno_diploma_%"),
      " contro ", v("Bagheria", "Y_GE65", "F", "almeno_diploma_%"), " sul diploma). ",
      "Fra i 25-49enni Bagheria è al ", v("Bagheria", "Y25-49", "T", "almeno_diploma_%"),
      " con almeno il diploma, contro il ", v(ETICHETTA_VICINATO, "Y25-49", "T", "almeno_diploma_%"),
      " del vicinato e il ", v("Sicilia", "Y25-49", "T", "almeno_diploma_%"), " della Sicilia: davanti ha ",
      paste(sopra, collapse = " e "), ", dietro ", paste(sotto, collapse = ", "), "."), LARGHEZZA),
    caption = didascalia_2b(
      lettura = paste0(
        "ogni riga è una classe d'età (in alto) o un territorio (in basso), e il segmento grigio unisce i due generi: la sua lunghezza è il divario. ",
        "Il pallino rosa è il valore femminile, quello blu il maschile; in alto la cifra accanto a ciascuno è il suo valore, in basso è stampata solo per Bagheria, la riga su fondo chiaro. ",
        "In basso il trattino nero è il valore di maschi e femmine insieme, ripetuto nella colonna a destra; le righe sono in ordine di quel valore sul diploma, e lo stesso ordine vale nel riquadro del terziario, dove quindi non è per valore. ",
        "Tutti e quattro i riquadri hanno la stessa scala. Le due misure sono annidate: «almeno il diploma» comprende chi ha anche un titolo terziario, quindi non si sommano. ",
        "Sul 9-24 il terziario è quasi nullo per costruzione, perché a 20 anni una laurea non può ancora esserci. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi, conteggi sommati prima delle quote. ",
        "Fra Bagheria, ", paste(sopra, collapse = " e "), " ci sono pochi punti, e i comuni che precedono Bagheria hanno in media circa ",
        residenti_sopra, " residenti della classe: l'ordine fra loro non è un risultato."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola istruzione per classe d'età e genere, anno ", anno_rif,
        ". Elaborazione: notebooks/genere.ipynb (data/processed/genere_titoli_eta.csv)."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "fig14_titoli_eta_genere", larghezza = LARGHEZZA, altezza = 27)
