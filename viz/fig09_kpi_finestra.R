# Figura 9 — il KPI della proposal in persone, e quanto ne resta.
# La domanda che un amministratore fa prima di firmare: "quante persone?". A sinistra la
# traduzione in teste (ogni quadratino sono dieci ragazze), a destra cosa ne resta quando
# la platea si restringe — perché chi avrà 15-24 anni nel 2029 è già nato, ed è di meno.
# Tutti i numeri arrivano dal notebook: qui si dispongono, non si ricalcolano.
#
# L'altra domanda — "come faccio a sapere se ha funzionato?" — sta in fig09b: è un
# pannello di metodo, parla di potenza statistica e non di persone, e teneva il titolo di
# questa figura a reggere due affermazioni separate da una virgola.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGH_FIGURA <- 28   # stessa misura del salvataggio: su questa il testo va a capo

UNITA <- 10   # ragazze per quadratino
COLONNE <- 20 # 20 x 15: il blocco è un po' più largo che alto, come il pannello che lo ospita,
              # così coord_equal lo fa crescere fino al bordo invece di lasciarlo piccolo in mezzo

base <- read_csv(file.path(PROCESSED, "genere_base_persone.csv"), show_col_types = FALSE)
persone <- read_csv(file.path(PROCESSED, "genere_gap_persone.csv"), show_col_types = FALSE)

popolazione <- base$popolazione_F_15_24[1]
occupate <- base$occupate_F_15_24[1]
anno <- base$anno[1]

# La platea futura è già nata: chi avrà 15-24 anni nel 2029 o nel 2034 è già residente.
# Stessa base demografica del waffle: se i due denominatori 2024 divergono, errore subito.
platea <- read_csv(file.path(PROCESSED, "genere_platea.csv"), show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", genere == "F")
stopifnot(platea$platea_2024 == popolazione)
# Il tetto a tasso costante vive nel notebook (genere_tetto_platea.csv): qui si legge
# e si dichiara nel sottotitolo del waffle, nessun ricalcolo.
tetto <- read_csv(file.path(PROCESSED, "genere_tetto_platea.csv"), show_col_types = FALSE) |>
  filter(genere == "F") |>
  arrange(orizzonte)
stopifnot(nrow(tetto) == 2, tetto$platea == c(platea$platea_2029, platea$platea_2034))
delta <- function(s) persone[["occupate in più (2024)"]][persone$scenario == s]

# Il KPI incontra la demografia: lordo, attrito, netto. Tutto dal notebook — qui si legge
# e si dispone. Il lordo deve essere lo stesso +40 del waffle, altrimenti i due pannelli
# starebbero raccontando due obiettivi diversi con lo stesso nome.
kpi <- read_csv(file.path(PROCESSED, "genere_kpi_netto.csv"), show_col_types = FALSE) |>
  arrange(orizzonte)
stopifnot(nrow(kpi) == 2,
          abs(kpi$kpi_lordo - delta("tasso femminile di Palermo")) < 1,
          kpi$platea == c(platea$platea_2029, platea$platea_2034))

# --- pannello A: le ragazze 15-24, un quadratino ogni dieci -------------------------
# Le classi sono cumulative e ordinate (oggi -> Palermo -> parità -> Italia -> il resto):
# i quadratini si ricavano dai cumulati arrotondati, così nessuno scarto si accumula.
CLASSI <- c("occupate oggi", "+ tasso di Palermo", "+ parità con i coetanei",
            "+ tasso nazionale", "non occupate")
cumulati <- c(occupate,
              occupate + delta("tasso femminile di Palermo"),
              occupate + delta("parità con i coetanei maschi di Bagheria"),
              occupate + delta("tasso femminile dell'Italia"),
              popolazione)
quadratini <- diff(c(0, round(cumulati / UNITA)))

etichette <- setNames(
  paste0(CLASSI, " (", migliaia(diff(c(0, cumulati))), ")"), CLASSI)

# Rampa ordinale su una tinta sola più il grigio del fondo: le classi hanno un ordine,
# non sono identità, quindi non serve — e non va usata — una palette categorica.
COLORI_WAFFLE <- setNames(
  c("#D55E00", "#EC8B4A", "#F6C4A0", "#FBE4D5", "#E4E4E1"), CLASSI)

griglia <- tibble(
    i = seq_len(sum(quadratini)),
    classe = factor(rep(CLASSI, quadratini), levels = CLASSI)
  ) |>
  mutate(colonna = (i - 1) %% COLONNE, riga = (i - 1) %/% COLONNE)

waffle <- ggplot(griglia, aes(colonna, -riga, fill = classe)) +
  geom_tile(width = 0.86, height = 0.86) +   # lo stacco fra i quadratini è il fondo, non un bordo
  scale_fill_manual(values = COLORI_WAFFLE, labels = etichette, name = NULL,
                    guide = guide_legend(ncol = 2, byrow = TRUE)) +
  coord_equal(clip = "off") +
  # Il restringimento della platea non si ripete qui: è il tema del pannello a fianco,
  # e ripeterlo allungava questo sottotitolo di due righe che patchwork scaricava come
  # spazio vuoto sopra l'altro pannello.
  labs(subtitle = paste0("Le ", migliaia(popolazione), " ragazze 15-24 di Bagheria, ",
                         anno, "\nun quadratino = ", UNITA, " ragazze"),
       x = NULL, y = NULL) +
  # La legenda sopra il waffle, non sotto: le cinque classi sono la chiave che rende
  # leggibili i quadratini, e in fondo alla figura si trovava dopo aver già rinunciato
  # a capire la rampa. Centrata sul pannello come in ogni altra figura.
  theme(axis.text = element_blank(), panel.grid = element_blank(),
        legend.position = "top")

# --- pannello B: il KPI meno l'attrito della platea ----------------------------------
# Lo stesso tasso obiettivo su una platea più piccola non produce lo stesso numero di
# occupate. Tre barre per orizzonte: quello che si promette oggi, quello che la platea si
# riprende, quello che resta alla scadenza. La lettura sta tutta nel confronto fra le due
# facce: al 2029 resta metà del KPI, al 2034 non resta niente.
# La corrispondenza colonna -> voce è esplicita: legata all'ordine delle colonne si
# romperebbe in silenzio il giorno in cui il notebook ne aggiunge una.
VOCI <- c(kpi_lordo = "obiettivo, platea di oggi",
          attrito_demografico = "quanto si restringe la platea",
          kpi_netto = "quello che resta")
COLORI_CASCATA <- setNames(c("#EC8B4A", "#9C9C9C", "#D55E00"), VOCI)

cascata <- kpi |>
  select(orizzonte, all_of(names(VOCI))) |>
  pivot_longer(-orizzonte, values_to = "valore") |>
  mutate(voce = factor(VOCI[name], levels = rev(VOCI)),
         faccia = paste("al", orizzonte))
stopifnot(!any(is.na(cascata$voce)))

attrito <- ggplot(cascata, aes(valore, voce, fill = voce)) +
  facet_wrap(~faccia, ncol = 1, scales = "free_y") +
  geom_vline(xintercept = 0, colour = "grey55", linewidth = 0.4) +
  geom_col(width = 0.62) +
  # L'etichetta esce dalla barra dalla parte in cui la barra cresce: dentro, una barra
  # corta come il netto del 2034 non la conterrebbe.
  geom_text(aes(label = sprintf("%+.0f", valore),
                hjust = ifelse(valore >= 0, -0.25, 1.25)),
            size = 3.4, fontface = "bold", colour = "grey20") +
  scale_fill_manual(values = COLORI_CASCATA, guide = "none") +
  scale_x_continuous(limits = c(-58, 58), breaks = seq(-40, 40, 20),
                     expand = expansion(mult = 0)) +
  scale_y_discrete(expand = expansion(add = c(0.75, 0.75))) +
  coord_cartesian(clip = "off") +
  labs(subtitle = paste0("E cosa ne resta quando la platea si restringe\n",
                         "le stesse +", round(kpi$kpi_lordo[1]),
                         " occupate, misurate sulla platea di ciascun anno"),
       x = "occupate in più rispetto al 2024", y = NULL)

# Due pannelli in fila. Impilarli in colonna non funziona: il waffle ha coord_equal e in
# mezza altezza collassa in un quadratino.
# La terza domanda — quanto deve essere grande un effetto perché la lettura lo veda — sta
# in fig09b: è un pannello di metodo, parla di potenza statistica e non di persone, e qui
# costringeva il titolo a reggere due affermazioni con una virgola.
figura <- (waffle | attrito) +
  plot_layout(widths = c(1, 0.9)) +
  plot_annotation(
    title = "Quaranta ragazze: il KPI è realistico, ma la demografia se lo riprende",
    subtitle = paste0(
      "Oggi ", occupate, " ragazze 15-24 su ", migliaia(popolazione),
      " lavorano. Allineare il tasso femminile a quello di Palermo vuol dire +",
      delta("tasso femminile di Palermo"), " occupate: il KPI realistico a 2-3 anni.\n",
      "La parità con i coetanei ne vorrebbe +", delta("parità con i coetanei maschi di Bagheria"),
      ", il tasso nazionale +", delta("tasso femminile dell'Italia"),
      ": quelli non sono obiettivi, sono la misura del problema.\n",
      "E il +", delta("tasso femminile di Palermo"), " non è quello che si vedrà alla scadenza: la platea 2029 è già nata ed è più piccola, così lo stesso tasso obiettivo\n",
      "ne vale ", sprintf("%+.0f", kpi$kpi_netto[1]), " al ", kpi$orizzonte[1], " e ", sprintf("%+.0f", kpi$kpi_netto[2]), " al ", kpi$orizzonte[2],
      ". Il target va scritto in tasso e non in teste, oppure riparametrato ogni anno sulla platea corrente."),
    caption = didascalia_4b(
      mostra = paste0(
        "il KPI della proposta tradotto in persone. A sinistra le ragazze di 15-24 anni di Bagheria nel ", anno,
        ", una per una, divise fra chi lavora oggi e i traguardi successivi; a destra lo stesso obiettivo confrontato con il restringimento della platea nei due orizzonti della proposta. ",
        "Non c'è nessun modello: è aritmetica sulla stessa popolazione, letta due volte. ",
        "Quanto debba essere grande un effetto perché una rilevazione riesca a vederlo sta in fig09b."),
      base = paste0(
        "N = ", migliaia(popolazione), " ragazze di 15-24 anni residenti a Bagheria nel ", anno,
        ", di cui ", occupate, " occupate. Le platee del ", kpi$orizzonte[1], " (", migliaia(platea$platea_2029),
        ") e del ", kpi$orizzonte[2], " (", migliaia(platea$platea_2034),
        ") contano ragazze già nate e già residenti oggi: sono un tetto che si restringe, non una previsione demografica, e non incorporano né migrazioni né nascite future. ",
        "Nessun intervallo di confidenza: sono conteggi censuari e non stime campionarie. ",
        "I quadratini del pannello sinistro sono arrotondati alla decina, mentre i totali in legenda no: la somma dei quadratini può quindi scostarsi di poche unità dai totali. ",
        "Le due misure dell'attrito demografico non coincidono e non vanno confuse, perché ciascuna si misura al tasso a cui la si applica: a tasso ", anno,
        " fermo la sola demografia toglie ", virgola(abs(tetto$delta_vs_2024[1]), 0), " occupate al ", kpi$orizzonte[1], " e ",
        virgola(abs(tetto$delta_vs_2024[2]), 0), " al ", kpi$orizzonte[2], " (lo scenario «non si fa niente»), mentre al tasso obiettivo di Palermo (",
        virgola(kpi$tasso_obiettivo_pct[1], 2), "%) ne toglie ", virgola(abs(kpi$attrito_demografico[1]), 0), " e ",
        virgola(abs(kpi$attrito_demografico[2]), 0), ", che è il numero disegnato nel pannello destro."),
      lettura = paste0(
        "nel pannello sinistro ogni quadratino vale ", UNITA,
        " ragazze e il blocco intero è la popolazione femminile 15-24. I colori sono una rampa ordinata su una tinta sola, non categorie: ",
        "il vermiglio pieno è chi lavora oggi, le tinte via via più chiare sono i traguardi successivi (allineamento a Palermo, parità con i coetanei, tasso nazionale) e il grigio è chi resta comunque fuori. ",
        "Le classi sono cumulative, quindi ogni fascia va letta come «e in più». ",
        "Nel pannello destro ogni faccia è un orizzonte e le tre barre si leggono in cascata: l'obiettivo sulla platea di oggi in arancio, quanto la platea si restringe in grigio (valore negativo, barra verso sinistra), quello che resta in vermiglio. ",
        "La riga verticale grigia è lo zero. La lettura sta tutta nel confronto fra le due facce."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, ", anno,
        ", e demografia per età singola per le platee future. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_base_persone.csv, genere_gap_persone.csv, genere_platea.csv, genere_tetto_platea.csv e genere_kpi_netto.csv)."),
      larghezza = LARGH_FIGURA),
    theme = tema_figura()
  )

salva(figura, "fig09_kpi_finestra", larghezza = LARGH_FIGURA, altezza = 27)
