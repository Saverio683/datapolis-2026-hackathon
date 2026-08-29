# Figura edu-07 — Bagheria dentro il suo gruppo di comuni simili, 2011.
# Claim del thread educazione (invariato): il deficit di ingresso nel lavoro compare anche
# fra comuni comparabili — occupazione 15-29 al 20,0% contro una mediana dei pari del
# 24,1% (gap -4,1 p.p.). Il matching resta descrittivo, mai causale.
#
# PERCHÉ QUESTA FORMA E NON UNDICI BARRE (figures/edu/11).
# Undici barre affiancate invitano a leggere una classifica, e con dieci pari una
# classifica è una precisione che il dato non ha: la domanda non è "che posto fa Bagheria"
# ma "sta dentro il gruppo o ne è fuori". La striscia di punti mostra la distribuzione per
# quello che è — dieci osservazioni, con la loro dispersione visibile — e la posizione di
# Bagheria si legge come collocazione dentro quella nuvola, non come rango.
# La seconda ragione è il DISEGNO dello studio, che le barre non raccontavano affatto:
# tre di questi indicatori sono serviti a scegliere i pari e due no. Sui primi Bagheria
# DEVE stare in mezzo — è così per costruzione — e vederlo è il controllo che il matching
# ha funzionato; solo sui secondi una posizione eccentrica significa qualcosa. Separare i
# due blocchi rende la figura autoverificante: il primo blocco è il collaudo, il secondo
# il risultato.
#
# Colore: Bagheria vermiglio, i pari grigi. Non sono territori con un'identità propria da
# distinguere l'uno dall'altro, sono la distribuzione di riferimento.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 27

pari <- read_csv(file.path(PROCESSED, "edu_matched_peers_2011.csv"), show_col_types = FALSE)

# Quali indicatori sono serviti a scegliere i pari e quali no: è la distinzione che regge
# tutta la lettura, e sta scritta qui perché il CSV non la porta.
# Fonte della divisione: il notebook dichiara che gli outcome occupazione e NEET non
# partecipano alla selezione, mentre il profilo educativo sì.
INDICATORI <- tibble::tribble(
  ~codice, ~nome,                             ~fascia, ~alto_favorevole, ~blocco,
  "I5",    "Uscita precoce dalla formazione", "15-24", FALSE,            "Profilo educativo: serve a scegliere i pari",
  "I6",    "Diploma o laurea",                "25-64", TRUE,             "Profilo educativo: serve a scegliere i pari",
  "I7",    "Titolo universitario",            "30-34", TRUE,             "Profilo educativo: serve a scegliere i pari",
  "L14",   "Occupazione giovanile",           "15-29", TRUE,             "Esiti: NON entrano nella scelta dei pari",
  "L4",    "NEET",                            "15-29", FALSE,            "Esiti: NON entrano nella scelta dei pari")

BLOCCHI <- unique(INDICATORI$blocco)

lungo <- pari |>
  select(nome_territorio, ruolo, all_of(INDICATORI$codice)) |>
  pivot_longer(all_of(INDICATORI$codice), names_to = "codice", values_to = "valore") |>
  inner_join(INDICATORI, by = "codice") |>
  mutate(blocco = factor(blocco, levels = BLOCCHI),
         riga = factor(codice, levels = rev(INDICATORI$codice)))

N_PARI <- sum(pari$ruolo == "Peer")
stopifnot(nrow(pari) == N_PARI + 1, sum(pari$ruolo == "Bagheria") == 1)

bagheria <- filter(lungo, ruolo == "Bagheria")
peer <- filter(lungo, ruolo == "Peer")

# Mediana dei pari (Bagheria esclusa: è il termine di paragone, non un membro del gruppo)
# e posizione di Bagheria dentro il gruppo. Entrambe si calcolano, non si scrivono.
riassunto <- peer |>
  summarise(mediana = median(valore), .by = c(codice, riga, blocco)) |>
  inner_join(select(bagheria, codice, valore_bagheria = valore), by = "codice") |>
  inner_join(select(INDICATORI, codice, alto_favorevole, nome, fascia), by = "codice") |>
  mutate(
    # Scarto in punti FAVOREVOLI: negativo significa sempre "Bagheria sta peggio della
    # mediana dei pari", su tutte e cinque le righe, qualunque sia il verso dell'indicatore.
    scarto_favorevole = ifelse(alto_favorevole, valore_bagheria - mediana,
                               mediana - valore_bagheria),
    # Il segno si prende dal valore GIÀ ARROTONDATO a un decimale, non da quello pieno:
    # sul diploma lo scarto vale −0,05 e stampava "−0", un segno meno davanti a zero che
    # dice il contrario di quello che è (Bagheria è sulla mediana, non sotto).
    scarto_etichetta = ifelse(
      abs(round(scarto_favorevole, 1)) < 0.05, "in linea con la mediana",
      paste0(ifelse(scarto_favorevole >= 0, "+", "−"),
             virgola(abs(scarto_favorevole), 1, taglia_zero = FALSE), " sulla mediana")))

# Il numero che il claim cita: se la pipeline cambiasse il gruppo di pari, il titolo
# smetterebbe di essere vero e la figura deve fermarsi invece di raccontarlo lo stesso.
l14 <- filter(riassunto, codice == "L14")
stopifnot(nrow(l14) == 1, abs(l14$scarto_favorevole - (-4.1)) < 0.15)

ETICHETTE <- riassunto |>
  mutate(testo = paste0(nome, "  ", fascia,
                        ifelse(alto_favorevole, "\n↑ meglio", "\n↓ meglio")))

figura <- ggplot(lungo, aes(valore, riga)) +
  facet_grid(blocco ~ ., scales = "free_y", space = "free_y",
             labeller = label_wrap_gen(width = 46)) +
  # I pari prima, così il pallino di Bagheria resta sopra quando i valori si sovrappongono.
  # Shape 21 con bordo bianco: fra i pari ci sono valori quasi identici (due comuni a
  # 45,1% sul diploma) e senza l'anello di fondo due pallini pieni diventano una macchia.
  geom_point(data = peer, size = 3.4, shape = 21, stroke = 0.9, fill = "grey72",
             colour = "white") +
  # La mediana dei pari: la tacca da cui si misura lo scarto del claim.
  geom_point(data = riassunto, aes(mediana, riga), shape = 124, size = 6.5,
             colour = "grey30") +
  geom_point(data = bagheria, size = 5, shape = 21, stroke = 0.9,
             fill = COLORI_TERRITORIO[["Bagheria"]], colour = "white") +
  # L'etichetta sopra il pallino e non di fianco: a sinistra, sulla riga del NEET, finiva
  # sopra la tacca della mediana e sopra due pari. Sopra non collide con niente, perché
  # la banda fra una riga e l'altra è vuota per costruzione.
  geom_text(data = riassunto,
            aes(valore_bagheria, riga,
                label = paste0(virgola(valore_bagheria, 1, "%"), "  (",
                               scarto_etichetta, ")")),
            nudge_y = 0.31, vjust = 0, size = 3.1, fontface = "bold",
            colour = COLORI_TERRITORIO[["Bagheria"]]) +
  scale_x_continuous(limits = c(-2, 52), breaks = seq(0, 50, 10),
                     labels = function(x) virgola(x, 0, "%"),
                     expand = expansion(mult = 0)) +
  scale_y_discrete(labels = setNames(ETICHETTE$testo, ETICHETTE$codice)) +
  labs(
    title = paste0("Fra ", N_PARI, " comuni siciliani costruiti per somigliarle, Bagheria è in mezzo sull'istruzione e in fondo sul lavoro"),
    subtitle = sommario(paste0(
      "Censimento 2011. Ogni pallino grigio è uno dei ", N_PARI,
      " comuni appaiati a Bagheria; il vermiglio è Bagheria, la tacca scura la mediana dei pari.\n",
      "I tre indicatori in alto sono serviti a scegliere i pari, quindi che Bagheria stia in mezzo è atteso: quel blocco è il collaudo dell'appaiamento, non un risultato.\n",
      "I due in basso non hanno partecipato alla selezione, e lì la posizione dice qualcosa: sull'occupazione giovanile Bagheria sta ",
      virgola(abs(l14$scarto_favorevole), 1), " punti sotto la mediana dei pari (",
      virgola(l14$valore_bagheria, 1), "% contro ", virgola(l14$mediana, 1), "%).\n",
      "Il divario non nasce dal confronto con Palermo o con la media regionale: resta anche fra comuni scelti per somigliarle."), LARGHEZZA),
    x = "valore dell'indicatore, censimento 2011", y = NULL,
    caption = didascalia(paste0(
      "Fonte: ISTAT, 8milaCensus, censimento 2011. Elaborazione: pipeline/edu (thread educazione) - data/processed/edu_matched_peers_2011.csv\n",
      "I pari sono i ", N_PARI, " comuni siciliani più vicini a Bagheria entro un caliper di popolazione, su struttura demografica, abitativa ed educativa. Gli esiti occupazione 15-29 e NEET 15-29 non entrano nella distanza di appaiamento: è ciò che rende la loro posizione informativa e non tautologica.\n",
      "Lo scarto è in punti favorevoli: valore di Bagheria meno mediana dei pari dove salire è meglio, l'opposto dove salire è peggio. Un valore negativo significa sempre \"Bagheria sta peggio\". La mediana è calcolata sui soli pari, Bagheria esclusa.\n",
      "Confronto DESCRITTIVO fra territori, mai causale: comuni simili su alcune variabili osservabili non sono un controllo sperimentale, e nulla qui autorizza a dire che l'appaiamento isoli l'effetto di una politica o di un tratto.\n",
      "Con ", N_PARI, " osservazioni la dispersione conta più della graduatoria: la figura mostra dove cade Bagheria dentro la nuvola, non che posto occupa. Le fasce d'età sono diverse per indicatore e scritte in ogni riga.\n",
      "Anno e fasce diversi dalle serie 2018-2024 delle altre figure del thread: è il gruppo di controllo storico, non un termine di paragone con il censimento permanente."),
      LARGHEZZA)
  ) +
  tema_figura() +
  theme(panel.grid.major.y = element_blank(),
        strip.text.y = element_text(angle = 0, hjust = 0),
        panel.spacing.y = unit(1.1, "lines"))

salva(figura, "edu_fig07_pari_2011", larghezza = LARGHEZZA, altezza = 17)
