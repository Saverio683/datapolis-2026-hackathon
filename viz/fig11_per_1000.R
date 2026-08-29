# Figura 11 — istruzione e lavoro sulla stessa fascia, su base 1.000, a farfalla.
# L'estrazione sta nel notebook («Su 1.000 ragazze»): sotto i 15 anni un diploma è
# impossibile, quindi le diplomate 9-24 sono le diplomate 15-24; il denominatore viene
# dalle età singole. Le due quote poggiano così sulla STESSA popolazione — ma non sono
# incatenate: l'incrocio titolo × condizione non esiste a livello comunale, e chi lavora
# non è un sottoinsieme di chi ha il diploma. Due misure parallele, mai stadi di un funnel.
# L'attainment letto dove il diploma è raggiungibile (18-24) sta in fig11b.
#
# Perché a farfalla e non più due facet affiancati (2026-08-28). Il titolo di questa figura
# è un confronto fra ragazze e ragazzi, e la versione a facet lo spezzava in due pannelli:
# per vedere che a Bagheria le diplomate sono 510 contro 462 diplomati l'occhio doveva
# saltare da un pannello all'altro tenendo a mente una lunghezza. Nelle ali i due valori
# stanno sulla stessa riga e condividono la base — è il motivo per cui le piramidi delle età
# funzionano: rispecchiate sì, ma con base comune, quindi il confronto resta corretto.
# In più l'inversione fra le due misure diventa una FORMA: le ali del diploma pendono a
# sinistra, quelle del lavoro a destra, e la forbice si vede invece di doverla dedurre.
#
# La scala è condivisa fra le due misure, non libera per pannello: che il lavoro sia un
# quinto del diploma è metà del finding, e due scale separate lo cancellerebbero.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 30   # stessa misura del salvataggio: su questa il testo va a capo

dati <- read_csv(file.path(PROCESSED, "genere_per_1000.csv"), show_col_types = FALSE)
anno_rif <- max(dati$anno)
dati <- filter(dati, anno == anno_rif)

ETICHETTA_VICINATO <- dati$nome_territorio[startsWith(dati$nome_territorio, "vicinato")][1]
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")
dati <- mutate(dati, nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)))

v <- function(terr, gen, colonna) dati[[colonna]][dati$nome_territorio == terr & dati$genere == gen]

# I titoli dei pannelli portano il verso: senza, le due farfalle sono due forme e il lettore
# deve dedurre da sé quale ala è più lunga. Le due frasi sono affermazioni sul dato, e più
# sotto ci sono i controlli che le reggono.
MISURE <- c(per_1000_diploma = "CON ALMENO IL DIPLOMA: l'ala delle ragazze è più lunga in tutti e cinque i territori",
            per_1000_occupati = "AL LAVORO: si inverte, l'ala dei ragazzi è più lunga ovunque, e a Bagheria è il doppio")

lungo <- dati |>
  pivot_longer(all_of(names(MISURE)), names_to = "misura", values_to = "per_1000") |>
  mutate(misura = factor(MISURE[misura], levels = MISURE),
         # Il segno è la sola cosa che fa la farfalla: le femmine a sinistra dello zero, i
         # maschi a destra. L'asse rimette i valori assoluti, così nessuno legge -510.
         segno = if_else(genere == "F", -1, 1),
         x = segno * per_1000)

#' Le due misure, appaiate per territorio: servono ai controlli e al sottotitolo.
confronto <- dati |>
  select(nome_territorio, genere, per_1000_diploma, per_1000_occupati) |>
  pivot_wider(names_from = genere, values_from = c(per_1000_diploma, per_1000_occupati)) |>
  mutate(scarto_lavoro = per_1000_occupati_M - per_1000_occupati_F,
         rapporto_lavoro = per_1000_occupati_M / per_1000_occupati_F)

# I titoli dei pannelli affermano due cose su tutti e cinque i territori: che sul diploma
# vincono le ragazze e che sul lavoro vincono i ragazzi. Se un'annata ribalta un territorio,
# meglio un errore che due frasi che continuano a dirlo.
stopifnot(all(confronto$per_1000_diploma_F > confronto$per_1000_diploma_M),
          all(confronto$per_1000_occupati_F < confronto$per_1000_occupati_M))

# Il primato di Bagheria è nel RAPPORTO, non nella differenza: in punti per mille lo scarto
# più largo è altrove. La versione a barre affiancate scriveva «a Bagheria è il più largo» e
# l'ambiguità passava; qui le ali mostrano lunghezze, cioè differenze, e la frase sbagliata
# si vedrebbe. Il controllo tiene la distinzione onesta.
bagheria <- confronto[confronto$nome_territorio == "Bagheria", ]
piu_largo <- confronto[which.max(confronto$scarto_lavoro), ]
stopifnot(bagheria$rapporto_lavoro == max(confronto$rapporto_lavoro),
          bagheria$scarto_lavoro < piu_largo$scarto_lavoro)

# I denominatori veri dietro la base 1.000: senza, «su 1.000 ragazze» non dice se dietro
# ci siano tremila persone o tre milioni, e su cinque territori la differenza è tutta lì.
N_TERRITORI <- paste(vapply(LIVELLI, function(t) paste0(t, " ",
    migliaia(round(v(t, "F", "pop_15_24"))), " ragazze e ",
    migliaia(round(v(t, "M", "pop_15_24"))), " ragazzi"), character(1)), collapse = "; ")

MASSIMO <- max(lungo$per_1000)

figura <- ggplot(lungo, aes(x, nome_territorio, fill = genere)) +
  facet_wrap(~misura, ncol = 1) +
  # La spina della farfalla: senza, le due ali sono due barre che si toccano per caso.
  geom_vline(xintercept = 0, colour = "grey35", linewidth = 0.5) +
  geom_col(width = 0.62) +
  geom_text(aes(label = per_1000, hjust = if_else(genere == "F", 1.25, -0.25)),
            size = 3.2, fontface = "bold", colour = "grey20") +
  scale_fill_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  # Valori assoluti sull'asse: la coordinata è firmata solo per costruire le ali.
  scale_x_continuous(limits = c(-1, 1) * MASSIMO * 1.22, breaks = seq(-600, 600, 200),
                     labels = abs, expand = expansion(0)) +
  labs(
    title = "Il diploma le ragazze lo raggiungono più dei ragazzi; il lavoro, la metà",
    subtitle = sommario(paste0(
      "Due misure sulla stessa popolazione di 15-24 anni, entrambe riportate a base 1.000 residenti dello stesso genere, ", anno_rif,
      ", su cinque territori: in alto quante persone hanno almeno il diploma, in basso quante lavorano. ",
      "La base 1.000 è una normalizzazione e non un conteggio, e serve a rendere confrontabili territori di taglia diversissima. ",
      "Ali a confronto sulla stessa riga: ragazze a sinistra della spina, ragazzi a destra, stessa scala nei due pannelli.\n",
      "A Bagheria su 1.000 ragazze ", v("Bagheria", "F", "per_1000_diploma"),
      " hanno almeno il diploma e ", v("Bagheria", "F", "per_1000_occupati"),
      " lavorano; su 1.000 coetanei, ", v("Bagheria", "M", "per_1000_diploma"), " e ",
      v("Bagheria", "M", "per_1000_occupati"), ". La farfalla si rovescia fra i due pannelli:\n",
      "è la forbice del thread (il titolo c'è, il lavoro no). Il primato di Bagheria è nel rapporto, non nella distanza: i ragazzi al lavoro sono ",
      virgola(bagheria$rapporto_lavoro, 1, "×", taglia_zero = FALSE),
      " le ragazze,\nil valore più alto del panel, ma in punti per mille l'ala si apre di più in ",
      piu_largo$nome_territorio, " (", piu_largo$scarto_lavoro, " contro ", bagheria$scarto_lavoro,
      "): a Bagheria è basso il livello femminile, non solo la distanza.\n",
      "Le due quote vivono sulla stessa popolazione (il conteggio dei diplomi 9-24 è per costruzione quello 15-24, perché nessuno ha un diploma prima), e restano\n",
      "due misure affiancate: quante delle diplomate lavorino il censimento comunale non lo dice, e chi lavora può non avere il diploma (fig11b per il 18-24)."), LARGHEZZA),
    x = paste0("per 1.000 residenti 15-24 dello stesso genere (", anno_rif, ")"), y = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "ogni riga è un territorio e la linea verticale scura al centro è la spina della farfalla, cioè lo zero. ",
        "L'ala rosa verso sinistra è il valore femminile, quella blu verso destra il maschile: la coordinata è negativa a sinistra solo per costruire la farfalla, e l'asse riporta i valori assoluti. ",
        "Le due ali partono entrambe dalla spina e condividono la base, quindi sono rispecchiate e non troncate, ed è ciò che rende corretto confrontarle a colpo d'occhio; ",
        "ogni ala ha però il suo denominatore (1.000 ragazze a sinistra, 1.000 ragazzi a destra), così le due lunghezze restano confrontabili anche dove le due popolazioni non sono uguali. ",
        "La scala orizzontale è la stessa nei due pannelli, apposta: che il lavoro sia una frazione del diploma è metà del finding, e due scale libere lo cancellerebbero. ",
        "Il rovesciamento della forma fra il pannello di sopra e quello di sotto è la forbice. ",
        "I due pannelli sono affiancati e non incatenati perché l'incrocio fra titolo di studio e condizione professionale non è pubblicato a livello comunale: chi lavora non è un sottoinsieme di chi ha il diploma, e non sono stadi di un percorso. ",
        "L'attainment letto sulla fascia in cui il diploma è già raggiungibile (18-24) sta in fig11b. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media dei cinque valori."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola istruzione (fascia 9-24 anni), tavola della condizione professionale (classe 15-24 anni) e demografia per età singola per i denominatori, anno ",
        anno_rif, ". Elaborazione: notebooks/genere.ipynb (data/processed/genere_per_1000.csv)."),
      larghezza = LARGHEZZA)
  )

# Figura a pannello unico (i due facet sono pannelli della stessa figura): titolo e
# sottotitolo sono quelli della figura, quindi vale il tema della figura.
figura <- figura + tema_figura() +
  # Dopo tema_figura(), che è un tema completo e rimpiazza quello accumulato.
  theme(panel.grid.major.y = element_blank(),
        strip.text = element_text(face = "bold", hjust = 0, size = rel(0.92),
                                  margin = margin(t = 6, b = 4)))

salva(figura, "fig11_per_1000", larghezza = LARGHEZZA, altezza = 22)
