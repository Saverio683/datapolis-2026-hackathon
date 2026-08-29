# Figura 2 — dove finiscono i giovani 15-24 di Bagheria, per genere.
# Il punto: la quota che resta fuori da lavoro e istruzione è quasi la stessa nei due
# generi, ma ci arriva da monte opposto — le ragazze dalle casalinghe, i ragazzi dall'«altra
# condizione».
#
# Perché un Sankey e non più la barra impilata che stava qui. Il «fuori da lavoro e
# istruzione» non è uno stato rilevato: è un'AGGREGAZIONE di quattro condizioni, e la barra
# poteva solo affermarlo con una graffa disegnata a mano sopra quattro segmenti contigui.
# Nel diagramma quell'aggregazione è la confluenza dei nastri: la definizione si vede invece
# di essere annotata. In più i tre nodi d'arrivo separano chi cerca lavoro da chi non lo
# cerca — il «gruppo invisibile» che nella barra viveva solo in caption — e i due nastri
# spessi che entrano nel nodo «fuori e non in cerca» hanno colori diversi nei due generi:
# è il finding, reso struttura invece che confronto fra due facet.
#
# Il confronto territoriale non entra nel diagramma — cinque territori di nastri sono
# illeggibili — e sta in fig02b, che scorpora la sola statistica che discrimina.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

ANNO <- 2024

# L'ordine è quello del percorso: prima chi è dentro lavoro o studio, poi chi è fuori ma
# cerca, poi chi è fuori e non cerca. Così gli stati che finiscono nello stesso nodo sono
# contigui e nessun nastro incrocia gli altri — le uniche pendenze che restano sono quelle
# della confluenza, che è ciò che il diagramma deve far vedere.
STATI <- c("occupati", "studenti", "in cerca", "casalinghe/i", "altra condizione", "pensione")
DESTINAZIONI <- c("dentro lavoro o studio", "fuori ma in cerca", "fuori e non in cerca")
stopifnot(setequal(STATI, names(COLORI_STATO)))

composizione <- read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio.csv"),
                         show_col_types = FALSE)

bag <- composizione |>
  filter(nome_territorio == "Bagheria", anno == ANNO, genere %in% c("F", "M")) |>
  mutate(stato = factor(stato, levels = STATI),
         destinazione = factor(destinazione, levels = DESTINAZIONI),
         genere = factor(genere, levels = names(COLORI_GENERE))) |>
  arrange(genere, stato)

# Il diagramma dà per scontato che i sei stati partizionino la popolazione e che ogni stato
# abbia un nodo d'arrivo: se una delle due cose salta, i nastri non tornano e la figura
# mente in silenzio. La partizione la garantisce l'assert del notebook; qui si controlla che
# la tabella sia arrivata intera.
stopifnot(nrow(bag) == 2 * length(STATI), !anyNA(bag$destinazione), !anyNA(bag$persone))

# --- Geometria -----------------------------------------------------------------------
# Le persone le conta il notebook: qui si calcolano solo le POSIZIONI, come fa fig04 con i
# vertici dei poligoni della mappa. R disegna, non trasforma.

TOTALE <- sum(bag$persone)
STACCO_GENERE <- 0.110 * TOTALE  # l'aria fra i due rami: ci deve stare l'etichetta del nodo
STACCO_STATO <- 0.014 * TOTALE   # fra stato e stato: separa senza spezzare la colonna
STACCO_DEST <- 0.055 * TOTALE    # il più largo: separa la confluenza e le sue etichette

# x dei nodi, e larghezza di ciascuno. La colonna degli stati è larga perché ci vivono
# dentro le etichette: le altre sono barrette, questa è la barra impilata di prima.
X <- c(totale = 0, genere = 0.58, stato = 1.62, destinazione = 2.92)
LARGHEZZA <- c(totale = 0.13, genere = 0.06, stato = 0.42, destinazione = 0.06)

#' Impila i blocchi di uno stadio dall'alto in basso e centra la pila sullo zero, così i
#' quattro stadi restano allineati anche se hanno stacchi diversi.
#' `stacco` è l'aria da lasciare DOPO ogni blocco (l'ultimo non ne ha bisogno).
impila <- function(df) {
  df |> mutate(passo = persone + stacco,
               sopra = (sum(passo) - last(stacco)) / 2 - (cumsum(passo) - passo),
               sotto = sopra - persone)
}

#' Le estremità dei nastri dentro un nodo: contigue, senza aria, a partire dal bordo
#' superiore del nodo che le raccoglie. Serve due volte — per le sorgenti dentro il nodo
#' che le emette e per gli arrivi dentro il nodo che li riceve.
dentro <- function(df, gruppi) {
  df |> mutate(sopra = cima - (cumsum(persone) - persone), sotto = sopra - persone,
               .by = all_of(gruppi))
}

#' Lo stacco da lasciare dopo ogni riga di uno stadio già ordinato per genere: quello fra i
#' due generi dove il genere cambia, quello dello stadio altrove, zero in fondo.
stacchi <- function(genere, dentro_stadio) {
  if_else(row_number() == length(genere), 0,
          if_else(genere != lead(genere), STACCO_GENERE, dentro_stadio))
}

nodo_totale <- tibble(persone = TOTALE, stacco = 0) |> impila()

nodo_genere <- bag |>
  summarise(persone = sum(persone), .by = genere) |>
  arrange(genere) |>
  mutate(stacco = c(STACCO_GENERE, 0)) |>
  impila()

nodo_stato <- bag |>
  mutate(stacco = stacchi(genere, STACCO_STATO)) |>
  impila()

# La quota del nodo si arrotonda UNA volta, sul conteggio del nodo: sommare le quote dei
# sei stati, già arrotondate al decimo dal notebook, dava 26,8% dove la fonte del proxy
# («fuori» = 6,87 + 19,87 = 26,74) dice 26,7 — e fig02 avrebbe smentito il resto del thread
# su un decimo. I conteggi, invece, si sommano prima di essere arrotondati: così i totali
# dei nodi restano quelli della platea di fig09 e non perdono una persona per strada.
nodo_dest <- bag |>
  summarise(persone = sum(persone), .by = c(genere, destinazione)) |>
  mutate(quota = 100 * persone / sum(persone), .by = genere) |>
  arrange(genere, destinazione) |>
  mutate(stacco = stacchi(genere, STACCO_DEST)) |>
  impila()

# --- Nastri --------------------------------------------------------------------------

PUNTI <- 60  # vertici per lato del poligono: sotto i ~40 la curva mostra le spezzate

#' Un nastro fra due bordi. Lo spessore è costante perché il flusso si conserva: nessuno si
#' perde per strada, e un nastro che si assottiglia direbbe il contrario. Il profilo è una
#' cosinusoide — la curva a S dei diagrammi alluvionali: parte e arriva orizzontale, così i
#' nastri si innestano nei nodi senza spigoli.
nastro <- function(x0, x1, y0_sopra, y0_sotto, y1_sopra, y1_sotto) {
  t <- seq(0, 1, length.out = PUNTI)
  s <- (1 - cos(pi * t)) / 2
  x <- x0 + (x1 - x0) * t
  tibble(x = c(x, rev(x)),
         y = c(y0_sopra + (y1_sopra - y0_sopra) * s,
               rev(y0_sotto + (y1_sotto - y0_sotto) * s)))
}

#' Da una tabella di flussi (una riga per nastro) ai vertici dei poligoni da disegnare.
#' `per` sono le colonne che appaiano sorgente e arrivo e che restano in uscita per il fill.
espandi <- function(sorgente, arrivo, x0, x1, per) {
  sorgente |>
    select(all_of(per), y0_sopra = sopra, y0_sotto = sotto) |>
    left_join(select(arrivo, all_of(per), y1_sopra = sopra, y1_sotto = sotto), by = per) |>
    mutate(nastro_id = row_number()) |>
    reframe(nastro(x0, x1, y0_sopra, y0_sotto, y1_sopra, y1_sotto),
            .by = c(all_of(per), nastro_id))
}

# Stadio 1 — il totale si divide fra i due generi: le due sorgenti stanno attaccate dentro
# il nodo del totale, e si staccano arrivando ai due nodi del genere.
sorgente_genere <- nodo_genere |>
  mutate(sopra = nodo_totale$sopra - (cumsum(persone) - persone), sotto = sopra - persone)

# Stadio 2 — ogni genere si apre nei sei stati; le sorgenti sono la suddivisione interna al
# nodo del genere, gli arrivi sono i blocchi dello stadio degli stati.
sorgente_stato <- nodo_stato |>
  left_join(select(nodo_genere, genere, cima = sopra), by = "genere") |>
  dentro("genere")

# Stadio 3 — i sei stati confluiscono nei tre nodi d'arrivo: gli arrivi sono la
# suddivisione interna al nodo di destinazione, nell'ordine degli stati.
arrivo_dest <- nodo_stato |>
  arrange(genere, destinazione, stato) |>
  left_join(select(nodo_dest, genere, destinazione, cima = sopra),
            by = c("genere", "destinazione")) |>
  dentro(c("genere", "destinazione"))

nastri_genere <- espandi(sorgente_genere, nodo_genere,
                         X[["totale"]] + LARGHEZZA[["totale"]], X[["genere"]], "genere")
nastri_stato <- espandi(sorgente_stato, nodo_stato,
                        X[["genere"]] + LARGHEZZA[["genere"]], X[["stato"]],
                        c("genere", "stato"))
nastri_dest <- espandi(nodo_stato, arrivo_dest,
                       X[["stato"]] + LARGHEZZA[["stato"]], X[["destinazione"]],
                       c("genere", "stato"))

# --- Etichette -----------------------------------------------------------------------

# Etichette di stato solo sui blocchi che le reggono. La soglia non è estetica: sotto,
# il testo è più alto del nastro e sconfina nell'aria bianca fra i blocchi, dove il bianco
# su bianco lo decapita — si legge peggio che non scrivendolo. Gli altri stati li dice la
# legenda, e le loro quote stanno nel sottotitolo.
SOGLIA_ETICHETTA <- 8

etichetta_stato <- nodo_stato |>
  filter(quota >= SOGLIA_ETICHETTA) |>
  mutate(y = (sopra + sotto) / 2,
         testo = paste0(stato, " · ", virgola(quota, suffisso = "%", taglia_zero = FALSE)))

etichetta_dest <- nodo_dest |>
  mutate(y = (sopra + sotto) / 2,
         testo = paste0(destinazione, "\n", migliaia(round(persone)), " · ",
                        virgola(quota, suffisso = "%", taglia_zero = FALSE)))

etichetta_genere <- nodo_genere |>
  mutate(testo = paste0(toupper(ETICHETTE_GENERE[as.character(genere)]), " · ",
                        migliaia(round(persone))),
         colore = COLORI_GENERE[as.character(genere)])

# --- Numeri del testo ------------------------------------------------------------------

quota_di <- function(territorio, stato_scelto, genere_scelto = "F") {
  composizione$quota[composizione$nome_territorio == territorio & composizione$anno == ANNO &
                       composizione$stato == stato_scelto & composizione$genere == genere_scelto]
}

#' Un nodo d'arrivo di Bagheria, per il sottotitolo: lettura dei valori già in figura.
nodo <- function(destinazione_scelta, genere_scelto) {
  nodo_dest[nodo_dest$destinazione == destinazione_scelta &
              nodo_dest$genere == genere_scelto, ]
}
# Il totale «fuori da lavoro e istruzione» viene dalla sua tabella, non da una somma qui:
# è il numero che citano CONTEXT-ale, la relazione e le altre figure, e deve essere identico.
# Le due quote dei nodi possono sommare un decimo in più: ogni arrotondamento è per conto suo,
# ed è la ragione della riga in caption.
fuori_totale <- read_csv(file.path(PROCESSED, "genere_fuori_lavoro_istruzione.csv"),
                         show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", anno == ANNO, genere %in% c("F", "M"))
fuori_di <- function(g) fuori_totale[fuori_totale$genere == g, ]

# Le casalinghe non sono spose: già coniugate dal registro (1° gennaio successivo al
# censimento) contro il conteggio delle casalinghe. Il floor tiene il claim prudente
# («almeno»): nulla dice che le coniugate siano tutte casalinghe.
casalinghe_n <- read_csv(file.path(PROCESSED, "genere_casalinghe.csv"), show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", anno == ANNO, genere == "F") |>
  pull(conteggio) |> round()
coniugate <- read_csv(file.path(PROCESSED, "genere_stato_civile.csv"), show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", genere == "F", fascia == "15-24") |>
  filter(anno == max(anno))
NUBILI_PCT <- floor(100 * (casalinghe_n - coniugate$gia_coniugate) / casalinghe_n)

# --- Il diagramma ----------------------------------------------------------------------

# I nodi degli stati sono l'unico strato mappato sulla scala del fill: quelli del genere
# portano i loro due colori come valore fisso (li dice già l'etichetta, una seconda legenda
# sarebbe rumore) e quelli d'arrivo sono grigi, perché un nodo d'arrivo non è una categoria
# ma una somma.
sankey <- ggplot() +
  geom_polygon(data = nastri_genere, aes(x, y, group = nastro_id),
               fill = COLORI_GENERE[as.character(nastri_genere$genere)], alpha = 0.5) +
  geom_polygon(data = nastri_stato, aes(x, y, group = nastro_id, fill = stato),
               alpha = 0.72, colour = "white", linewidth = 0.2) +
  geom_polygon(data = nastri_dest, aes(x, y, group = nastro_id, fill = stato),
               alpha = 0.72, colour = "white", linewidth = 0.2) +
  geom_rect(data = nodo_totale,
            aes(xmin = X[["totale"]], xmax = X[["totale"]] + LARGHEZZA[["totale"]],
                ymin = sotto, ymax = sopra),
            fill = "grey30") +
  geom_rect(data = nodo_genere,
            aes(xmin = X[["genere"]], xmax = X[["genere"]] + LARGHEZZA[["genere"]],
                ymin = sotto, ymax = sopra),
            fill = COLORI_GENERE[as.character(nodo_genere$genere)]) +
  geom_rect(data = nodo_stato,
            aes(xmin = X[["stato"]], xmax = X[["stato"]] + LARGHEZZA[["stato"]],
                ymin = sotto, ymax = sopra, fill = stato),
            colour = "white", linewidth = 0.3) +
  geom_rect(data = nodo_dest,
            aes(xmin = X[["destinazione"]],
                xmax = X[["destinazione"]] + LARGHEZZA[["destinazione"]],
                ymin = sotto, ymax = sopra),
            fill = "grey30") +
  # Il totale sta dentro la sua barra, ruotato: è l'unico nodo abbastanza alto da reggerlo,
  # e messo di fianco ruberebbe larghezza ai nastri.
  geom_text(data = nodo_totale,
            aes(x = X[["totale"]] + LARGHEZZA[["totale"]] / 2, y = (sopra + sotto) / 2),
            label = paste0(migliaia(round(TOTALE)), " giovani 15-24 anni"),
            angle = 90, colour = "white", fontface = "bold", size = 3.6) +
  geom_text(data = etichetta_genere,
            aes(x = X[["genere"]], y = sopra, label = testo, colour = colore),
            hjust = 0, vjust = -0.55, fontface = "bold", size = 3.4) +
  geom_text(data = etichetta_stato,
            aes(x = X[["stato"]] + LARGHEZZA[["stato"]] / 2, y = y, label = testo),
            colour = "white", fontface = "bold", size = 2.6) +
  geom_text(data = etichetta_dest,
            aes(x = X[["destinazione"]] + LARGHEZZA[["destinazione"]] + 0.05, y = y,
                label = testo),
            hjust = 0, vjust = 0.5, lineheight = 1.05, size = 3, colour = "grey20") +
  scale_fill_manual(values = COLORI_STATO, breaks = STATI) +
  scale_colour_identity() +
  # Il margine a destra è lo spazio delle etichette d'arrivo: senza, vengono tagliate.
  scale_x_continuous(limits = c(0, X[["destinazione"]] + 0.92), expand = expansion(0)) +
  scale_y_continuous(expand = expansion(mult = c(0.05, 0.07))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = NULL, y = NULL)

# Figura a pannello unico: titolo e sottotitolo sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- sankey +
  labs(
    title = "Stessa quota fuori da lavoro e istruzione, ragioni opposte: una ragazza su sette è casalinga",
    subtitle = paste0(
      "Dal totale ai due generi, dai sei stati della condizione professionale ai tre esiti: lo spessore di ogni nastro è il numero di persone.\n",
      "Fuori da lavoro e istruzione — il proxy del NEET calcolabile a scala comunale — c'è più di un giovane su quattro in entrambi i generi: ",
      virgola(fuori_di("F")$quota_pct), "% delle\nragazze (", migliaia(fuori_di("F")$persone),
      ") e ", virgola(fuori_di("M")$quota_pct), "% dei ragazzi (", migliaia(fuori_di("M")$persone),
      "). Ma i due nastri arrivano da monte opposto: sono casalinghe il ",
      virgola(quota_di("Bagheria", "casalinghe/i")), "% delle ragazze contro l'",
      virgola(quota_di("Bagheria", "casalinghe/i", "M")), "% dei ragazzi,\nquasi il triplo dell'incidenza nazionale (",
      virgola(quota_di("Italia", "casalinghe/i")), "%), mentre l'«altra condizione» pesa il ",
      virgola(quota_di("Bagheria", "altra condizione", "M")), "% sui ragazzi contro il ",
      virgola(quota_di("Bagheria", "altra condizione")), "% sulle ragazze.\nE le casalinghe non sono spose: le già coniugate 15-24 sono ",
      coniugate$gia_coniugate, " contro ", casalinghe_n, " casalinghe — almeno l'", NUBILI_PCT,
      "% è nubile. Il terzo nodo — fuori anche dalla\nricerca di lavoro — raccoglie ",
      migliaia(round(nodo(DESTINAZIONI[3], "F")$persone)), " ragazze e ",
      migliaia(round(nodo(DESTINAZIONI[3], "M")$persone)), " ragazzi: è il gruppo che nessuna politica attiva intercetta, perché non si presenta a nessuno sportello."),
    caption = paste(
      "Fonte: ISTAT, Censimento permanente della popolazione - tavola condizione professionale, classe 15-24 anni,", paste0(ANNO, "."),
      "\nI tre nodi d'arrivo sono la convenzione di repo («fuori da lavoro e istruzione» = tutti meno occupati e studenti), spezzata in due secondo la ricerca di lavoro:",
      "\nnon è il NEET ISTAT 15-29, che a livello comunale esiste solo al 2011 (fig08). Il diagramma è una partizione della stessa popolazione a un solo anno,",
      "\nnon una transizione: il censimento non segue le persone, e nessun nastro va letto come un percorso individuale nel tempo.",
      "\nLa condizione è autodichiarata al censimento: marcatore del carico di cura, non sua misura diretta. Ogni quota è arrotondata al decimo per conto suo:",
      "\nsommare due nodi può dare un decimo in più del totale citato qui sopra, che viene da genere_fuori_lavoro_istruzione.csv come nel resto del thread.",
      "\nStato civile da DCIS_POPRES1 (1° gennaio 2025), fonte diversa dal censimento: denominatori coincidenti alla singola unità; non osserva convivenze né maternità.",
      "\nIl confronto territoriale sulla quota di casalinghe - la sola statistica che discrimina Bagheria dal panel - sta in fig02b.",
      "\nElaborazione: notebooks/genere.ipynb - data/processed/genere_composizione_stato_dettaglio.csv (persone e nodo d'arrivo),",
      "\ngenere_fuori_lavoro_istruzione.csv (totale del proxy), genere_casalinghe.csv e genere_stato_civile.csv (nubili)"),
    x = NULL, y = NULL
  ) +
  tema_figura() +
  # Dopo tema_figura(), non prima: un tema completo rimpiazza quello accumulato, e messa
  # sopra questa riga spariva. Il diagramma non ha assi — le posizioni sono geometria, non
  # una scala da leggere — e la griglia taglierebbe i nastri.
  theme(axis.text = element_blank(), axis.ticks = element_blank(),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank())

salva(figura, "fig02_composizione_stato", larghezza = 30, altezza = 19)
