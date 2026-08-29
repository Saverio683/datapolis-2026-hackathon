# Figura 2b — la quota di casalinghe fra le ragazze 15-24, sui cinque territori.
# Il punto: non è un'anomalia comunale. Nel vicinato la quota è la stessa o più alta, a
# Palermo poco sotto, in Italia un terzo: il carico di cura è un tratto di zona, e una
# politica che lo tratta come un problema di Bagheria sbaglia bacino.
#
# Scorporo di fig02 (2026-08-28): stava come striscia a fianco del Sankey. Da sola regge —
# è l'unica statistica del thread che separa Bagheria dal panel, e nel Sankey era il nastro
# vermiglio delle ragazze. Il diagramma dice DA DOVE arriva il «fuori da lavoro e
# istruzione» femminile, questa dice QUANTO LONTANO arriva lo stesso fenomeno.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 26   # stessa misura del salvataggio: su questa il testo va a capo
ANNO <- 2024
STATO <- "casalinghe/i"

composizione <- read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio.csv"),
                         show_col_types = FALSE)
# Il vicinato aggregato è un territorio a sé, non uno dei cinque comuni: conteggi sommati e
# poi la quota (nel notebook), non media delle cinque quote.
vicinato <- read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio_vicini.csv"),
                     show_col_types = FALSE)
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]

# L'ordine è geografico, non per valore: dal comune al paese, così la riga si legge come uno
# zoom che si allarga e la discesa dei valori è il finding, non l'effetto dell'ordinamento.
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))

dati <- bind_rows(composizione, vicinato) |>
  filter(anno == ANNO, stato == STATO, genere %in% c("F", "M"),
         nome_territorio %in% LIVELLI) |>
  mutate(nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)))

territori <- dati |>
  filter(genere == "F") |>
  mutate(colore = COLORI[as.character(nome_territorio)])
stopifnot(nrow(territori) == length(LIVELLI), !anyNA(territori$colore))

quota_di <- function(territorio, genere_scelto = "F") {
  dati$quota[dati$nome_territorio == territorio & dati$genere == genere_scelto]
}

# Le persone dietro la quota di Bagheria: la quota da sola non dice se il bacino di un
# intervento è di 40 o di 400 persone, ed è la prima domanda di chi deve progettarlo.
casalinghe_n <- read_csv(file.path(PROCESSED, "genere_casalinghe.csv"), show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", anno == ANNO, genere == "F") |>
  pull(conteggio) |> round()

RAPPORTO <- quota_di("Bagheria") / quota_di("Italia")

# I denominatori: quante ragazze 15-24 stanno sotto ciascuna quota. Senza, una percentuale
# su cinque territori di taglia diversissima non dice se il bacino è di decine o di migliaia.
platea <- read_csv(file.path(PROCESSED, "genere_platea.csv"),
                   col_types = cols(territorio = "c", nome_territorio = "c",
                                    genere = "c", .default = "d"))
N_TERRITORI <- paste(
  vapply(ORDINE, function(t) paste0(t, " ",
           migliaia(platea$platea_2024[platea$nome_territorio == t & platea$genere == "F"])),
         character(1)),
  collapse = "; ")

figura <- ggplot(territori, aes(quota, nome_territorio, colour = colore)) +
  geom_segment(aes(x = 0, xend = quota, yend = nome_territorio), linewidth = 1.4) +
  geom_point(size = 4.6) +
  geom_text(aes(label = virgola(quota, suffisso = "%", taglia_zero = FALSE)),
            hjust = -0.35, size = 3.6, fontface = "bold", colour = "grey20") +
  scale_colour_identity() +
  # Aria a destra per l'etichetta del valore, che sta fuori dal pallino.
  scale_x_continuous(expand = expansion(mult = c(0, 0.16))) +
  labs(
    title = "Le casalinghe non sono un'anomalia di Bagheria: il vicinato sta anche peggio",
    subtitle = paste0(
      "Quota di ragazze 15-24 che si dichiarano casalinghe, ", ANNO, ". A Bagheria sono ",
      virgola(quota_di("Bagheria")), "% (", casalinghe_n, " ragazze) e nei cinque comuni\n",
      "più vicini ",  virgola(quota_di(ETICHETTA_VICINATO)),
      "%: il livello non si ferma al confine comunale. Palermo è a ",
      virgola(quota_di("Palermo")), "%, la Sicilia a ", virgola(quota_di("Sicilia")),
      "%, l'Italia a ", virgola(quota_di("Italia")), "%, quindi Bagheria vale ",
      virgola(RAPPORTO, 1, "×", taglia_zero = FALSE),
      "\nl'incidenza nazionale. Fra i ragazzi la stessa condizione pesa l'",
      virgola(quota_di("Bagheria", "M")), "% a Bagheria e lo ",
      virgola(quota_di("Italia", "M")), "% in Italia: il divario è di zona, la condizione è di genere."),
    x = NULL, y = NULL,
    caption = didascalia_4b(
      mostra = paste0(
        "quota di ragazze di 15-24 anni che al censimento si dichiarano casalinghe, in percentuale delle coetanee residenti, anno ",
        ANNO, ", su cinque territori. La condizione è autodichiarata: è un marcatore del carico di cura, non la sua misura diretta, ",
        "e non dice nulla su chi sia la persona accudita. Da dove arrivi questa quota dentro la popolazione 15-24 di Bagheria, e dove porti, lo mostra fig02."),
      base = paste0(
        "Denominatori (ragazze 15-24 residenti al ", ANNO, "): ", N_TERRITORI,
        ". A Bagheria il numeratore è di ", casalinghe_n, " ragazze. ",
        "Per il vicinato i conteggi dei cinque comuni sono sommati prima della quota, non è la media delle cinque quote. ",
        "Nessun intervallo di confidenza: sono conteggi censuari e non stime campionarie, e nessun record è escluso. ",
        "Un solo anno, quindi la figura non misura una tendenza: la serie completa sta in genere_composizione_stato_dettaglio.csv."),
      lettura = paste0(
        "ogni riga è un territorio e la lunghezza del segmento è la quota, ripetuta in cifre a destra del pallino. ",
        "L'ordine delle righe è geografico e non per valore, dal comune al paese: la discesa da Bagheria all'Italia è il finding, non l'effetto dell'ordinamento. ",
        "I colori sono quelli che i territori portano in tutta la cartella (Bagheria in vermiglio, il vicinato in verde acqua, Palermo in viola, la Sicilia in ambra, l'Italia in grigio) e non codificano nessuna variabile in più. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, ", ANNO, ". ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_composizione_stato_dettaglio.csv, genere_composizione_stato_dettaglio_vicini.csv per il vicinato aggregato, genere_casalinghe.csv per il conteggio e genere_platea.csv per i denominatori)."),
      larghezza = LARGHEZZA)
  ) +
  # Le righe orizzontali della griglia duplicherebbero i segmenti del lollipop.
  theme(panel.grid.major.y = element_blank())

# Figura a pannello unico: titolo e sottotitolo sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- figura + tema_figura()

salva(figura, "fig02b_casalinghe_territori", larghezza = LARGHEZZA, altezza = 17)
