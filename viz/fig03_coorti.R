# Figura 3 — ritenzione di coorte 2021-2024 per genere.
# Il punto: il drenaggio ha tempi diversi per ragazzi e ragazze.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Larghezza dichiarata una volta: il testo va a capo sulla stessa misura del salvataggio.
LARGHEZZA <- 24

# Il vicinato aggregato come quinta riga: coorti dei cinque comuni sommate e poi il
# rapporto (nel notebook), stessa metrica della fig07.
vicinato <- read_csv(file.path(PROCESSED, "genere_coorti_vicini.csv"), show_col_types = FALSE)
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")

dati <- bind_rows(
    read_csv(file.path(PROCESSED, "genere_coorti.csv"), show_col_types = FALSE),
    vicinato
  ) |>
  mutate(nome_territorio = factor(nome_territorio, levels = rev(LIVELLI))) |>
  pivot_wider(id_cols = c(nome_territorio, coorte), names_from = genere,
              values_from = `ritenzione_%`, names_prefix = "rit_")

# I denominatori: quante persone c'erano nella coorte del 2021, cioè la base di ogni
# rapporto disegnato. Le età singole della fig07 sono la stessa fonte, raggruppate qui
# nelle tre classi quinquennali che la figura mostra.
enne_coorti <- read_csv(file.path(PROCESSED, "genere_ritenzione_eta.csv"),
                        show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", eta_2021 >= 15, eta_2021 <= 29) |>
  mutate(coorte = paste0(5 * (eta_2021 %/% 5), "-", 5 * (eta_2021 %/% 5) + 4, " nel 2021")) |>
  summarise(n = sum(n_2021), .by = c(coorte, genere)) |>
  arrange(coorte, genere)
N_COORTI <- paste(sprintf("%s: %s femmine e %s maschi",
                          sub(" nel .*", "", unique(enne_coorti$coorte)),
                          migliaia(enne_coorti$n[enne_coorti$genere == "F"]),
                          migliaia(enne_coorti$n[enne_coorti$genere == "M"])),
                  collapse = "; ")

# Serve al sottotitolo: la coorte in cui Bagheria e vicinato divergono.
COORTE_CHIAVE <- "25-29 nel 2021"
ritenzione_F <- function(territorio) {
  dati$rit_F[dati$nome_territorio == territorio & dati$coorte == COORTE_CHIAVE]
}

# I numeri sui punti: senza, i pallini dicono l'ordine e non il valore, e la scala è
# talmente stretta (96-105) che a occhio due righe diverse sembrano uguali. L'etichetta va
# al lato ESTERNO del segmento - il valore basso a sinistra, l'alto a destra - così le due
# non si toccano mai, nemmeno dove i punti coincidono (Sicilia, 25-29): lì il pareggio si
# vede perché i due numeri stampati sono identici, che è più chiaro dell'anello.
# `ties.method = "first"` è il rompi-parità: a valori uguali la F (prima riga del pivot)
# va a sinistra e la M a destra, sempre nello stesso verso.
# Testo in inchiostro e non nel colore del genere: il rosa a corpo 2,9 non regge i 4,5:1
# sul bianco (vedi la nota sul footer in theme.R). A dire il genere ci pensa il pallino
# che l'etichetta tocca.
STACCO <- 0.22  # in unità d'asse: quanto l'etichetta sta lontano dal centro del punto

etichette <- dati |>
  pivot_longer(c(rit_F, rit_M), names_prefix = "rit_", names_to = "genere",
               values_to = "valore") |>
  mutate(destra = rank(valore, ties.method = "first") == 2,
         .by = c(nome_territorio, coorte)) |>
  mutate(x_testo = valore + if_else(destra, STACCO, -STACCO),
         allineamento = if_else(destra, 0, 1))

figura <- ggplot(dati, aes(y = nome_territorio)) +
  geom_vline(xintercept = 100, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_segment(aes(x = rit_F, xend = rit_M, yend = nome_territorio),
               colour = "grey70", linewidth = 1.1) +
  # Diametri diversi: dove i due valori coincidono (Sicilia, 25-29) si vede un anello
  # invece di un punto solo, che sembrerebbe un dato mancante.
  geom_point(aes(x = rit_F, colour = "F"), size = 4.2) +
  geom_point(aes(x = rit_M, colour = "M"), size = 2.8) +
  geom_text(data = etichette,
            aes(x = x_testo, hjust = allineamento,
                label = virgola(valore, 1, taglia_zero = FALSE)),
            size = 2.9, fontface = "bold", colour = "grey25") +
  facet_wrap(~coorte, ncol = 1) +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  # L'espansione fa spazio alle etichette agli estremi: senza, il 104,7 dell'Italia e il
  # 96,3 di Bagheria finiscono tagliati dal bordo del pannello.
  scale_x_continuous(labels = function(x) virgola(x, 1, "%"),
                     expand = expansion(mult = 0.09)) +
  labs(
    title = "I ragazzi se ne vanno presto, le ragazze dopo i 25 anni",
    subtitle = sommario(paste0(
      "Quota della coorte del 2021 ancora residente tre anni dopo, in percentuale della coorte di partenza (chi aveva 15-19 anni nel 2021 ne ha 18-22 nel 2024), ",
      "per genere e per classe quinquennale d'età, su cinque territori. È una misura netta di saldo: comprende sia chi parte sia chi arriva, non distingue le destinazioni ",
      "e incorpora l'aggiustamento post-censuario delle stime di popolazione; lo stesso fenomeno per età singola, che individua la finestra esatta, sta in fig07.\n",
      "Sotto il 100% la coorte si è ridotta. Bagheria resta sotto il livello italiano in ogni cella, ma la perdita femminile si concentra dopo i 25 anni, ",
      "l'età in cui il vantaggio educativo dovrebbe convertirsi in lavoro.\n",
      "Sulla coorte ", sub(" nel .*", "", COORTE_CHIAVE),
      " le ragazze di Bagheria scendono a ", virgola(ritenzione_F("Bagheria"), 1, "%"),
      ", nel vicinato salgono a ", virgola(ritenzione_F(ETICHETTA_VICINATO), 1, "%"),
      ": è un tratto di Bagheria, non della zona."), LARGHEZZA),
    x = "residenti nel 2024 in % della coorte 2021", y = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "la riga tratteggiata verticale a 100% è la parità: a sinistra la coorte si è ridotta, a destra è cresciuta. ",
        "Ogni riga è un territorio e ogni pannello una coorte. Il segmento grigio unisce i due generi dello stesso territorio, e la sua lunghezza è il divario. ",
        "Il pallino grande rosa è il valore femminile, quello piccolo blu il maschile: i diametri sono diversi apposta, così dove i due valori coincidono si vede un anello e non un dato mancante. ",
        "I numeri stampati ai lati del segmento sono gli stessi valori dei pallini che toccano, messi all'esterno per non sovrapporsi. ",
        "I valori sono quote grezze, senza lisciamento, e la scala è stretta di pochi punti: si leggono i pattern rispetto al riferimento nazionale, non i decimali. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi, con le coorti sommate prima del rapporto: è il rapporto del blocco, non la media dei cinque rapporti."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, età singole, anni 2021 e 2024. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_coorti.csv, genere_coorti_vicini.csv e genere_ritenzione_eta.csv per i denominatori)."),
      larghezza = LARGHEZZA)
  )

# Figura a pannello unico: titolo e sottotitolo qui sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- figura + tema_figura()

salva(figura, "fig03_coorti", larghezza = LARGHEZZA, altezza = 21)
