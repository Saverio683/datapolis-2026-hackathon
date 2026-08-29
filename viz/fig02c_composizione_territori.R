# Figura 2c — la composizione della condizione professionale 15-24, per territorio e genere.
# Il punto: il buco di occupazione di Bagheria è simile nei due generi (-9 punti sull'Italia
# fra le ragazze, -10 fra i ragazzi), ma la quota non evapora — riappare, e in due posti
# diversi. Fra le ragazze quasi tutta fra le casalinghe (+8,8 punti), fra i ragazzi
# nell'«altra condizione» (+7,6). E non è che a Bagheria si studi di più: la quota di
# studentesse è più bassa di quella italiana.
#
# Perché barre al 100% e non un altro lollipop come fig02b. Il lollipop misura UNA statistica
# per volta e non può mostrare il compenso: se a Bagheria le casalinghe stanno nove punti
# sopra l'Italia, quei nove punti li sta togliendo a qualcos'altro, e quale sia è il finding.
# La somma a 100 lo rende visibile per costruzione — è la stessa partizione di fig02, letta
# su cinque territori invece che su uno.
#
# fig02 (Sankey) dice DA DOVE arriva il «fuori da lavoro e istruzione» di Bagheria e dove
# porta, ma su un territorio solo: cinque territori di nastri sono illeggibili. fig02b tiene
# il dettaglio sulla sola quota di casalinghe. Questa è il confronto territoriale sull'intera
# composizione, che finora mancava.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

ANNO <- 2024

# --- Ordine delle categorie ------------------------------------------------------------
# In una barra impilata solo i segmenti ANCORATI A UN BORDO sono confrontabili fra righe:
# gli altri partono da un offset diverso in ogni riga e l'occhio non può misurarli. Quindi
# l'ordine non è quello narrativo di fig02 — è dettato da quali due segmenti devono reggere
# il confronto: «occupati» al bordo sinistro, «casalinghe/i» al destro.
# «altra condizione» sta penultima, contigua alle casalinghe: fra i ragazzi le casalinghe
# valgono l'1-2% ovunque, quindi il suo bordo destro è quasi allineato e nel pannello dei
# maschi si legge lo stesso. «pensione» (0,1-0,5%) va in mezzo, dove non toglie spazio.
STATI <- c("occupati", "studenti", "in cerca", "pensione", "altra condizione", "casalinghe/i")
stopifnot(setequal(STATI, names(COLORI_STATO)))

# Etichette chiare sui fondi scuri, scure sui due colori chiari della palette: su #56B4E9 e
# #E69F00 il bianco sta sotto 2,5:1 e sparisce. Il testo è bold, quindi vale la soglia 3:1.
TESTO_BIANCO <- c("occupati", "studenti", "casalinghe/i")

# Sotto questa quota l'etichetta è più larga del segmento e sconfina su quelli accanto, dove
# si legge peggio che non scrivendola. Stessa logica di fig02, soglia più bassa perché qui i
# segmenti da confrontare sono più stretti (le casalinghe in Italia sono al 4,6%).
SOGLIA_ETICHETTA <- 4.5

# --- Dati -------------------------------------------------------------------------------

COLONNE <- c("nome_territorio", "anno", "genere", "stato", "quota")

composizione <- read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio.csv"),
                         show_col_types = FALSE)
# Il vicinato aggregato è un territorio a sé, non uno dei cinque comuni: conteggi sommati e
# poi la quota (nel notebook), non media delle cinque quote.
vicinato <- read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio_vicini.csv"),
                     show_col_types = FALSE)
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]

# Ordine geografico, non per valore: dal comune al paese, così la colonna si legge come uno
# zoom che si allarga. Rovesciato sull'asse y perché ggplot dispone dal basso.
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")

dati <- bind_rows(select(composizione, all_of(COLONNE)), select(vicinato, all_of(COLONNE))) |>
  filter(anno == ANNO, genere %in% c("F", "M"), nome_territorio %in% LIVELLI) |>
  mutate(nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)),
         stato = factor(stato, levels = STATI))

# La figura dà per scontato che i sei stati partizionino la popolazione di ogni riga: se una
# riga non chiude, la barra mente in silenzio — sarebbe lunga come le altre ma su un
# denominatore diverso. La partizione la garantisce l'assert del notebook; qui si controlla
# che le due tabelle siano arrivate intere e che nessuna riga si sia persa per strada.
stopifnot(nrow(dati) == length(LIVELLI) * 2 * length(STATI), !anyNA(dati$quota))
chiusura <- dati |> summarise(totale = sum(quota), .by = c(nome_territorio, genere))
stopifnot(abs(chiusura$totale - 100) < 0.5)

# Le quote pubblicate sono arrotondate al decimo e possono sommare a 100,1: normalizzarle
# allinea i bordi destri delle dieci barre, che in un grafico al 100% è il riferimento di
# tutta la lettura. Lo scarto è sotto il millesimo, invisibile. Le ETICHETTE restano il
# numero della fonte: la geometria si aggiusta, il numero scritto no.
barre <- dati |>
  arrange(genere, nome_territorio, stato) |>
  mutate(q = quota / sum(quota), .by = c(nome_territorio, genere))

# Le etichette si posizionano sullo stesso cumulato delle barre, non su una seconda
# geometria: position_stack(reverse) impila nell'ordine dei livelli, e questo lo replica.
etichette <- barre |>
  mutate(x = cumsum(q) - q / 2, .by = c(nome_territorio, genere)) |>
  filter(quota >= SOGLIA_ETICHETTA) |>
  mutate(colore = if_else(stato %in% TESTO_BIANCO, "white", "grey20"),
         testo = virgola(quota, suffisso = "%", taglia_zero = FALSE))

# --- La graffa del proxy -----------------------------------------------------------------
# Gli stati oltre «studenti» sono, tutti insieme, il «fuori da lavoro e istruzione» del
# thread. Per come sono ordinati formano un blocco contiguo appoggiato al bordo destro:
# la graffa lo aggrega senza che serva una seconda geometria, ed è lo stesso totale che in
# fig02 è la confluenza dei nastri nei due nodi «fuori». Sta solo su Bagheria — è il
# soggetto, e cinque graffe per pannello direbbero cinque volte la stessa cosa.
# Che le due graffe partano quasi dallo stesso punto è il finding di fig02 reso visibile
# qui di scorcio: la quota fuori è la stessa nei due generi, la sua composizione no.
DENTRO <- c("occupati", "studenti")

# Il totale NON si somma qui dalle quote in figura: quelle sono arrotondate al decimo una
# per una e la loro somma dà 26,8 dove il resto del thread cita 26,7. Il numero arriva dalla
# tabella che lo pubblica, come in fig02. Lo stopifnot verifica che il bordo sinistro della
# graffa — che invece nasce dalle barre — cada dove quel numero dice: se le due fonti
# divergessero oltre l'arrotondamento, la graffa indicherebbe un tratto e ne scriverebbe un
# altro, ed è un errore che guardando il PNG non si vede.
fuori <- read_csv(file.path(PROCESSED, "genere_fuori_lavoro_istruzione.csv"),
                  show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", anno == ANNO, genere %in% c("F", "M"))

graffa <- barre |>
  filter(nome_territorio == "Bagheria", !stato %in% DENTRO) |>
  summarise(x0 = 1 - sum(q), .by = genere) |>
  left_join(fuori, by = "genere")
stopifnot(nrow(graffa) == 2, abs(100 * (1 - graffa$x0) - graffa$quota_pct) < 0.25)

# Bagheria è l'ultimo livello di rev(LIVELLI), quindi la riga in cima: la graffa le sta
# sopra, appena fuori dalla barra, con due denti che scendono a chiudere il tratto.
LARGHEZZA_BARRA <- 0.72
Y_GRAFFA <- length(LIVELLI) + LARGHEZZA_BARRA / 2 + 0.26
DENTE <- 0.17

denti <- graffa |> reframe(x = c(x0, 1), .by = genere)

etichetta_graffa <- graffa |>
  mutate(testo = paste0("fuori da lavoro e istruzione: ",
                        virgola(quota_pct, suffisso = "%", taglia_zero = FALSE), " — ",
                        migliaia(persone), if_else(genere == "F", " ragazze", " ragazzi")))

# --- Numeri del testo --------------------------------------------------------------------
# Nessuna cifra scritta a mano: ogni numero del titolo e del sottotitolo si rilegge qui.

q <- function(territorio, stato_scelto, genere_scelto) {
  dati$quota[dati$nome_territorio == territorio & dati$stato == stato_scelto &
               dati$genere == genere_scelto]
}
#' Quanti punti Bagheria sta sopra (o sotto) l'Italia su uno stato, in un genere.
scarto <- function(stato_scelto, genere_scelto) {
  q("Bagheria", stato_scelto, genere_scelto) - q("Italia", stato_scelto, genere_scelto)
}

BUCO_F <- -scarto("occupati", "F")
BUCO_M <- -scarto("occupati", "M")

# --- Figura -------------------------------------------------------------------------------

PANNELLI <- c(
  F = "RAGAZZE - dove Bagheria perde occupazione, la ritrova fra le casalinghe",
  M = "RAGAZZI - lo stesso buco, ma riappare nell'«altra condizione»"
)

figura <- ggplot(barre, aes(q, nome_territorio, fill = stato)) +
  geom_col(position = position_stack(reverse = TRUE), width = 0.72) +
  geom_text(aes(x = x, y = nome_territorio, label = testo, colour = colore),
            data = etichette, inherit.aes = FALSE, size = 2.9, fontface = "bold") +
  geom_segment(aes(x = x0, xend = 1, y = Y_GRAFFA, yend = Y_GRAFFA), data = graffa,
               inherit.aes = FALSE, colour = "grey35", linewidth = 0.4) +
  geom_segment(aes(x = x, xend = x, y = Y_GRAFFA, yend = Y_GRAFFA - DENTE), data = denti,
               inherit.aes = FALSE, colour = "grey35", linewidth = 0.4) +
  # Allineata a destra sul 100%: centrata sulla graffa sforerebbe il pannello, perché
  # l'etichetta è più larga del tratto che descrive.
  geom_text(aes(x = 1, y = Y_GRAFFA + 0.18, label = testo), data = etichetta_graffa,
            inherit.aes = FALSE, hjust = 1, vjust = 0, size = 3.1, colour = "grey25") +
  facet_wrap(~genere, ncol = 1, labeller = labeller(genere = PANNELLI)) +
  scale_fill_manual(values = COLORI_STATO, breaks = STATI) +
  scale_colour_identity() +
  scale_x_continuous(expand = expansion(0), breaks = seq(0, 1, 0.25),
                     labels = paste0(seq(0, 100, 25), "%")) +
  # Aria in cima per la graffa e la sua etichetta, che stanno fuori dalla barra.
  scale_y_discrete(expand = expansion(add = c(0.55, 1.55))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(
    title = paste0("Alle ragazze di Bagheria mancano ", round(BUCO_F),
                   " punti di occupazione: riappaiono quasi tutti fra le casalinghe"),
    subtitle = paste0(
      "Composizione della condizione professionale, 15-24 anni, ", ANNO,
      ". Ogni barra somma 100: un territorio per riga, ordine geografico.\n",
      # Niente articolo davanti alle quote: «al 8,2%» vuole l'apostrofo, «al 9,6%» no, e
      # la forma giusta dipenderebbe da una cifra che arriva dai dati.
      "Fra le ragazze Bagheria sta a ", virgola(q("Bagheria", "occupati", "F")),
      "% di occupate contro ", virgola(q("Italia", "occupati", "F")),
      "% dell'Italia, mentre le casalinghe pesano ",
      virgola(q("Bagheria", "casalinghe/i", "F")), "% contro ",
      virgola(q("Italia", "casalinghe/i", "F")), "%:\n",
      virgola(BUCO_F), " punti persi da una parte, ", virgola(scarto("casalinghe/i", "F")),
      " ritrovati dall'altra. E non è che a Bagheria si studi di più - le studentesse sono ",
      virgola(q("Bagheria", "studenti", "F")), "% contro ",
      virgola(q("Italia", "studenti", "F")), "%.\n",
      "Sui ragazzi il buco di occupazione è quasi identico (", virgola(BUCO_M),
      " punti), ma la quota riemerge nell'«altra condizione» (+",
      virgola(scarto("altra condizione", "M")), "), non fra le casalinghe.\n",
      "Stesso divario, destinazioni diverse. Il vicinato segue Bagheria o sta peggio su entrambe le voci: ",
      "il confine comunale non è dove cambia il fenomeno."),
    x = NULL, y = NULL,
    caption = paste(
      "Fonte: ISTAT, Censimento permanente della popolazione - tavola condizione professionale, classe 15-24 anni,", paste0(ANNO, "."),
      "\nOrdine delle categorie: in una barra impilata solo i segmenti ancorati a un bordo sono confrontabili fra righe - gli altri partono da un offset diverso in ogni riga.",
      "\nPer questo 'occupati' sta a sinistra e 'casalinghe/i' a destra: sono le due voci del confronto. Le altre quattro si leggono dentro un territorio, non fra territori.",
      "\nEtichette solo sui segmenti che le reggono (quota >=", paste0(virgola(SOGLIA_ETICHETTA), "%):"),
      "sotto, il testo è più largo del segmento e sconfina su quelli accanto.",
      "\nLe quote sono arrotondate al decimo alla fonte e possono sommare a 100,1: la barra normalizza per allineare i bordi, l'etichetta resta il numero pubblicato.",
      "\nLa graffa aggrega i quattro stati oltre 'studenti' - la convenzione di repo ('fuori da lavoro e istruzione' = tutti meno occupati e studenti), non il",
      "\nNEET ISTAT 15-29, che a scala comunale esiste solo al 2011. Il totale viene da genere_fuori_lavoro_istruzione.csv: sommare qui le quote già arrotondate darebbe un decimo in più.",
      "\nLa condizione è autodichiarata al censimento: marcatore del carico di cura, non sua misura diretta. Ordine geografico, non per valore.",
      "\nVicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media delle cinque quote.",
      "\nLa stessa partizione su Bagheria sola, con i tre esiti aggregati e i conteggi, sta in fig02; il dettaglio sulle sole casalinghe in fig02b.",
      "\nElaborazione: notebooks/genere.ipynb - data/processed/genere_composizione_stato_dettaglio.csv,",
      "\ngenere_composizione_stato_dettaglio_vicini.csv (vicinato aggregato)")
  ) +
  tema_figura() +
  theme(
    # L'asse resta senza griglia: le righe verticali attraverserebbero i colori delle barre.
    # Le tacche in fondo bastano a collocare il bordo sinistro della graffa, che è l'unico
    # punto della figura che non ha un'etichetta accanto.
    panel.grid = element_blank(),
    strip.text = element_text(face = "bold", colour = "grey15", size = rel(0.98), hjust = 0,
                              margin = margin(t = 6, b = 6)),
    panel.spacing.y = unit(1.1, "lines")
  )

salva(figura, "fig02c_composizione_territori", larghezza = 28, altezza = 20)
