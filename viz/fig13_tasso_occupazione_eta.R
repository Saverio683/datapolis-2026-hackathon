# Figura 13 — il tasso di occupazione classe per classe. Il resto della cartella guarda i
# 15-24, e da lì il ritardo di Bagheria sembra un problema di ingresso nel lavoro. Messo
# accanto alle altre tre classi, non lo è: il divario con la Sicilia in punti si allarga
# fino ai 50-64, cioè fra chi nel mercato del lavoro c'è già dentro da trent'anni.
#
# Le quattro classi sono tutte quelle che esistono: il censimento permanente a livello
# comunale pubblica la condizione professionale solo su 15-24, 25-49, 50-64 e 65+ (e sul
# totale 15+, che le somma e qui non si disegna). Niente 15-34, niente quinquennali.
#
# Il pannello dei 65+ resta anche se è quasi piatto: toglierlo per far respirare gli altri
# tre lascerebbe credere che la scala arrivi a zero per scelta grafica e non perché dopo i
# 65 anni non lavora quasi nessuno, in nessuno dei quattro territori.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 26   # stessa misura del salvataggio: su questa il testo va a capo

nomi <- read_csv(file.path(PROCESSED, "territori.csv"),
                 col_types = cols(.default = "c"))

# Il 2020 non c'è nella tavola: sulla 15-24 la fonte non pubblica nessuna riga, sulle
# altre classi pubblica solo il denominatore. `complete()` rimette la riga vuota, che
# serve a interrompere le linee sul buco invece di farle passare sopra (theme.R).
# `grezzo` tiene anche numeratore e denominatore: al grafico servono solo i tassi, alla
# didascalia servono le numerosità, e buttarle via qui vorrebbe dire riaprire il file dopo.
grezzo <- read_csv(file.path(PROCESSED, "tasso_occupazione_eta.csv"),
                   col_types = cols(territorio = "c", eta = "c", classe = "c",
                                    genere = "c", .default = "d")) |>
  filter(genere == "T", eta != "Y_GE15") |>
  left_join(nomi[c("territorio", "nome_territorio")], by = "territorio") |>
  mutate(nome_territorio = factor(nome_territorio, levels = ORDINE),
         classe = factor(classe, levels = c("15-24", "25-49", "50-64", "65+")))

dati <- grezzo |>
  select(classe, nome_territorio, anno, tasso_occupazione) |>
  complete(classe, nome_territorio, anno = full_seq(anno, 1))

ANNO <- max(dati$anno)
PRIMO <- min(dati$anno)
ANCORE <- c(PRIMO, 2021, ANNO)  # le annate etichettate sull'asse: prima, ripresa, ultima

foto <- dati |>
  filter(anno == ANNO) |>
  pivot_wider(names_from = nome_territorio, values_from = tasso_occupazione) |>
  mutate(gap_pp = Bagheria - Sicilia, gap_rel = 100 * (Bagheria / Sicilia - 1))

# Il finding regge solo se Bagheria sta sotto la Sicilia dappertutto: se una classe
# passasse sopra, il titolo direbbe una cosa che la figura non mostra.
stopifnot(all(foto$gap_pp < 0))

# Le numerosità delle quattro classi a Bagheria nell'ultima annata: sono i denominatori
# di ogni punto disegnato sulla linea vermiglia.
N_CLASSI <- grezzo |>
  filter(nome_territorio == "Bagheria", anno == max(anno)) |>
  arrange(classe) |>
  mutate(testo = paste0(classe, " ", migliaia(round(popolazione)))) |>
  pull(testo) |> paste(collapse = ", ")

PIU_LARGO <- foto$classe[which.min(foto$gap_pp)]     # il divario più ampio in punti
PIU_LARGO_REL <- foto$classe[which.min(foto$gap_rel)] # ...e in percentuale sulla base
riga <- function(cl) foto[foto$classe == cl, ]
GIOVANI <- riga("15-24")
LARGO <- riga(PIU_LARGO)

# Il cuneo Bagheria-Sicilia dentro ogni pannello: è la quantità di cui parla il titolo,
# e disegnarla evita che il lettore la debba misurare a occhio fra due linee.
cuneo <- dati |>
  filter(nome_territorio %in% c("Bagheria", "Sicilia")) |>
  pivot_wider(names_from = nome_territorio, values_from = tasso_occupazione)

# Il divario sta nell'intestazione del pannello e non dentro: a 25-49 e 50-64 la linea
# dell'Italia sale fino a ridosso del 75% e qualunque annotazione in alto le finisce sotto.
# In testata è anche il posto giusto per leggerlo — è la didascalia del pannello, non un
# dato in più sul grafico.
testata <- foto |>
  transmute(classe, pannello = paste0(classe, "   ", virgola(gap_pp, 1), " pp vs Sicilia"))
LIVELLI <- testata$pannello[order(testata$classe)]

con_testata <- function(tabella) {
  tabella |>
    left_join(testata, by = "classe") |>
    mutate(pannello = factor(pannello, levels = LIVELLI))
}
dati <- con_testata(dati)
cuneo <- con_testata(cuneo)

figura <- ggplot(dati, aes(asse_2020(anno), tasso_occupazione, colour = nome_territorio)) +
  geom_ribbon(data = cuneo, aes(x = asse_2020(anno), ymin = Bagheria, ymax = Sicilia),
              inherit.aes = FALSE, fill = COLORI_TERRITORIO[["Bagheria"]], alpha = 0.10) +
  geom_line(aes(linewidth = nome_territorio == "Bagheria")) +
  geom_point(size = 1.5) +
  facet_wrap(~ pannello, nrow = 1) +
  scale_colour_manual(values = COLORI_TERRITORIO) +
  scale_linewidth_manual(values = c(`TRUE` = 1.3, `FALSE` = 0.8), guide = "none") +
  # `scala_2020()` etichetta tutte e sei le annate: qui i pannelli sono quattro e le
  # etichette si sovrapponevano fra loro e da un pannello all'altro. Le posizioni restano
  # quelle compresse di `asse_2020()`, si dicono solo i tre estremi — la serie è monotona
  # e la figura si legge sui livelli, non annata per annata.
  scale_x_continuous(breaks = asse_2020(ANCORE), labels = ANCORE,
                     expand = expansion(mult = c(0.06, 0.06))) +
  scale_y_continuous(limits = c(0, 80), breaks = seq(0, 75, 25),
                     labels = function(x) virgola(x, 0, "%")) +
  buco_2020(y = 40, dati$anno, dati$tasso_occupazione) +
  labs(
    title = "Il ritardo di Bagheria sull'occupazione accompagna tutta la vita lavorativa",
    subtitle = sommario(paste0(
      "Tasso di occupazione, cioè occupati in percentuale della popolazione della stessa classe d'età, dal ", PRIMO, " al ", ANNO,
      ", su quattro territori e su tutte e quattro le classi d'età pubblicate a livello comunale, maschi e femmine insieme (la stessa tavola aperta per genere sta in fig13b). ",
      "Il tasso sta sulla popolazione della classe e non sulle sole forze di lavoro, quindi comprende studenti e inattivi: è la ragione per cui la classe 15-24 resta strutturalmente bassa in tutti i territori.\n",
      "In punti il divario con la Sicilia è più stretto sui giovani (",
      virgola(GIOVANI$gap_pp, 1), " pp) e tocca il massimo sui ", PIU_LARGO, " (",
      virgola(LARGO$gap_pp, 1), " pp): il ritardo comincia al primo ingresso e prosegue per tutta la carriera. Sulla base ",
      "bassa dei 15-24 però quei ", virgola(GIOVANI$gap_pp, 1), " pp sono\n",
      "il ", virgola(abs(GIOVANI$gap_rel), 0), "% dell'occupazione della classe: in ",
      "termini relativi la più distante dalla Sicilia resta proprio il ", PIU_LARGO_REL, "."), LARGHEZZA),
    x = NULL, y = NULL, colour = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "ogni pannello è una classe d'età, e la cifra nella sua intestazione è il divario di Bagheria rispetto alla Sicilia in punti percentuali nell'ultima annata. ",
        "L'area vermiglio chiaro dentro ogni pannello è il cuneo fra Bagheria e la Sicilia: la sua altezza è la distanza fra le due linee, non un intervallo di confidenza. ",
        "Bagheria è in vermiglio a tratto pieno perché è il soggetto, i tre riferimenti sono a tratto sottile. ",
        "La striscia grigia verticale fra il 2019 e il 2021 occupa l'annata mancante: il 2020 manca alla fonte (sulla classe 15-24 non esiste nessuna riga, sulle altre solo il denominatore) e nessun valore è interpolato. ",
        "Sull'asse orizzontale sono etichettate solo la prima annata, il 2021 e l'ultima, perché con quattro pannelli affiancati sei etichette si sovrappongono; le posizioni restano quelle di tutte le annate. ",
        "Le quattro classi sono le uniche pubblicate a livello comunale dal censimento permanente: la fascia 15-34 del bando non è ricostruibile da qui, e il totale 15+ resta fuori perché somma le quattro classi invece di affiancarsi a loro."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, ", PRIMO, "-", ANNO,
        ". Elaborazione: pipeline/build.py (data/processed/tasso_occupazione_eta.csv, che contiene anche il dettaglio per genere)."),
      larghezza = LARGHEZZA)) +
  tema_figura() +
  theme(panel.spacing.x = unit(1.1, "lines"))

salva(figura, "fig13_tasso_occupazione_eta", larghezza = LARGHEZZA, altezza = 19)
