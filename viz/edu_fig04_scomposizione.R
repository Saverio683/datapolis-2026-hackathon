# Figura edu-04 — da dove viene il cambiamento 2018-2024, in persone.
# Claim del thread educazione (invariato): fra 2018 e 2024 le persone in cerca calano di
# circa 663, gli occupati crescono di 222 e gli studenti di 203; gli inattivi non studenti
# calano soltanto di circa 102. Il recupero è molto più forte sulla ricerca che sul nucleo
# inattivo. "Fuori da lavoro e studio" è composito e non è una quinta condizione.
#
# PERCHÉ QUESTA FORMA E NON LE BARRE DELLA SOLA VARIAZIONE (figures/edu/07).
# Una barra per stato dice quanto è cambiato, non perché. E qui il perché è la metà del
# risultato: la popolazione 15-24 di Bagheria si è ristretta nel periodo, quindi una parte
# di ogni variazione è pura aritmetica del denominatore. Sugli inattivi la differenza è
# sostanziale — dei ~102 in meno, ~66 li toglie la demografia e solo ~35 il cambio di
# tasso — e una barra sola la nasconde, facendo sembrare un calo quello che è quasi
# soltanto una coorte più piccola. La cascata separa le due cause e mette il netto come
# terza barra, la stessa grammatica già usata in fig09 del thread genere.
# Le due cause sono barre affiancate e non impilate: hanno segni opposti nella stessa riga
# (sugli occupati la demografia toglie mentre il tasso aggiunge) e una pila con segni
# misti si legge male o non si legge.
#
# "Fuori da lavoro e studio" non ha un pannello: è la somma di "in cerca" e "inattivi non
# studenti", e affiancarla alle sue componenti conterebbe le stesse persone due volte.
# Sta nel sottotitolo come totale, che è il posto giusto per un aggregato.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 28

scomposizione <- read_csv(file.path(PROCESSED, "edu_change_decomposition_2018_2024.csv"),
                          show_col_types = FALSE)

COMPOSITO <- "fuori_lavoro_studio"
stati <- filter(scomposizione, metrica != COMPOSITO)
aggregato <- filter(scomposizione, metrica == COMPOSITO)
stopifnot(nrow(stati) == 4, nrow(aggregato) == 1)

# La scomposizione deve chiudere: i due effetti sommano alla variazione in persone. Se la
# pipeline cambiasse convenzione, le tre barre di ogni pannello smetterebbero di stare in
# relazione fra loro e la figura non se ne accorgerebbe da sola.
stopifnot(all(abs(stati$effetto_popolazione + stati$effetto_tasso -
                    stati$variazione_conteggio) < 0.01))
# Gli effetti di TASSO devono sommare a zero: le quattro quote fanno 100% in entrambe le
# annate, quindi a coorte ferma quello che un stato guadagna un altro lo perde. È
# l'invariante vera della scomposizione — le variazioni in persone NON sommano a zero,
# perché la coorte si è ristretta, e la loro somma è esattamente l'effetto demografico.
stopifnot(abs(sum(stati$effetto_tasso)) < 0.02,
          abs(sum(stati$effetto_popolazione) - sum(stati$variazione_conteggio)) < 0.02)
# L'aggregato è la somma delle sue due componenti, non uno stato in più.
stopifnot(abs(aggregato$variazione_conteggio -
                sum(stati$variazione_conteggio[stati$metrica %in%
                                                 c("in_cerca", "inattivi_non_studenti")])) < 0.01)

# La coorte che fa da denominatore alla scomposizione: senza, «meno 130 persone» non dice
# se sia un decimo o un centesimo della fascia.
coorte <- read_csv(file.path(PROCESSED, "edu_youth_states_2018_2024.csv"),
                   show_col_types = FALSE) |>
  filter(territorio_nome == "Bagheria")
enne_coorte <- function(a) coorte$popolazione[coorte$anno == a]

DA <- unique(stati$anno_iniziale)
A <- unique(stati$anno_finale)
stopifnot(length(DA) == 1, length(A) == 1)

# Le tre voci di ogni pannello. La corrispondenza colonna -> voce è esplicita: legata
# all'ordine delle colonne si romperebbe in silenzio se il notebook ne aggiungesse una.
VOCI <- c(effetto_popolazione = "la coorte si restringe",
          effetto_tasso = "il tasso cambia",
          variazione_conteggio = "variazione netta")
# Le due cause in grigio e sky, il netto in vermiglio: il netto è il numero che il claim
# cita, le cause sono la sua spiegazione. Nessuna scala categorica per un ordine.
COLORI_VOCE <- setNames(c("#9C9C9C", "#56B4E9", "#D55E00"), VOCI)

# I pannelli in ordine di |variazione netta|: chi si è mosso di più sta in alto, e gli
# inattivi — il finding — finiscono in fondo, dove la barra corta si legge come corta.
ordine_stati <- stati$metrica_label[order(-abs(stati$variazione_conteggio))]

cascata <- stati |>
  select(metrica_label, all_of(names(VOCI))) |>
  pivot_longer(-metrica_label, values_to = "persone") |>
  mutate(voce = factor(VOCI[name], levels = rev(VOCI)),
         pannello = factor(metrica_label, levels = ordine_stati))
stopifnot(!any(is.na(cascata$voce)), !any(is.na(cascata$pannello)))

# I limiti tengono conto dell'etichetta, non solo della barra: il valore esce dalla barra
# dal lato in cui cresce, e sul -601 di "in cerca" serve spazio a sinistra.
ESTREMO <- max(abs(cascata$persone)) * 1.24

netto <- function(m) stati$variazione_conteggio[stati$metrica == m]
tasso <- function(m) stati$effetto_tasso[stati$metrica == m]
popolazione <- function(m) stati$effetto_popolazione[stati$metrica == m]

figura <- ggplot(cascata, aes(persone, voce, fill = voce)) +
  facet_wrap(~pannello, ncol = 2, scales = "free_y") +
  geom_vline(xintercept = 0, colour = "grey55", linewidth = 0.4) +
  geom_col(width = 0.6) +
  # L'etichetta esce dalla barra dalla parte in cui la barra cresce: dentro, una barra
  # corta come l'effetto di tasso sugli inattivi non la conterrebbe.
  geom_text(aes(label = sprintf("%+.0f", persone),
                hjust = ifelse(persone >= 0, -0.22, 1.22)),
            size = 3.2, fontface = "bold", colour = "grey20") +
  scale_fill_manual(values = COLORI_VOCE, guide = "none") +
  scale_x_continuous(limits = c(-ESTREMO, ESTREMO), breaks = seq(-600, 600, 300),
                     labels = function(x) migliaia(x), expand = expansion(mult = 0)) +
  scale_y_discrete(expand = expansion(add = c(0.72, 0.72))) +
  coord_cartesian(clip = "off") +
  labs(
    title = "Il recupero dei giovani di Bagheria è quasi tutto ricerca di lavoro che si spegne",
    subtitle = sommario(paste0(
      "Variazione ", DA, "-", A, " dei 15-24enni di Bagheria in PERSONE, scomposta in due cause: quante ne toglie o ne aggiunge il restringersi della coorte,\n",
      "e quante il cambiamento del tasso. Le due sommano alla variazione netta. Chi cerca lavoro cala di ",
      migliaia(round(abs(netto("in_cerca")))), " persone e quasi tutto è cambiamento di tasso (",
      migliaia(round(tasso("in_cerca"))), ");\n",
      "gli inattivi non studenti calano di appena ", migliaia(round(abs(netto("inattivi_non_studenti")))),
      ", e di questi ", migliaia(round(abs(popolazione("inattivi_non_studenti")))),
      " li toglie soltanto la coorte più piccola: il tasso si muove di ",
      migliaia(round(tasso("inattivi_non_studenti"))), " persone.\n",
      "Il nucleo che non cerca non si è riattivato: si è quasi solo rimpicciolito con la demografia."), LARGHEZZA),
    x = paste0("persone, ", DA, " → ", A), y = NULL,
    caption = didascalia_4b(
      mostra = paste0(
        "scomposizione della variazione del numero di 15-24enni di Bagheria in ciascuno dei quattro stati della condizione professionale, fra il ",
        DA, " e il ", A, ", in persone. Ogni variazione è divisa in due parti: quanto è dovuto al restringimento della coorte e quanto al cambiamento del tasso. ",
        "È aritmetica, non un modello: non attribuisce cause al di là del denominatore."),
      base = paste0(
        "Coorte di riferimento: ", migliaia(round(enne_coorte(DA))), " residenti di 15-24 anni nel ", DA,
        " e ", migliaia(round(enne_coorte(A))), " nel ", A, ". ",
        "Scomposizione shift-share sui due estremi del periodo: l'effetto popolazione è la variazione della coorte a tasso ", DA,
        " fermo, l'effetto tasso è la variazione del tasso applicata alla coorte ", A, "; la somma è esatta e non approssimata, con controllo nel notebook. ",
        "Il 2020 non è pubblicato ma non entra qui, perché la scomposizione confronta i due estremi del periodo. ",
        "I quattro stati sono esaustivi, ma le variazioni in persone non sommano a zero, perché la coorte 15-24 si è ristretta nel periodo: la loro somma è esattamente l'effetto demografico complessivo. ",
        "A sommare a zero sono invece gli effetti di tasso, perché le quattro quote fanno 100% in entrambe le annate. ",
        "Le persone sono ricostruite dalle quote pubblicate e possono avere frazioni di unità: qui sono arrotondate all'intero. ",
        "«Fuori da lavoro e studio» non ha un pannello perché è la somma di «in cerca» e «inattivi non studenti»: vale ",
        sprintf("%+.0f", aggregato$variazione_conteggio), " persone, ma affiancarlo alle sue componenti le conterebbe due volte."),
      lettura = paste0(
        "ogni pannello è uno stato e le barre si leggono in cascata: il grigio è l'effetto del restringimento della coorte, il colore è l'effetto del cambiamento del tasso, e la barra vermiglia è la variazione totale, cioè la somma esatta delle due. ",
        "La riga verticale allo zero separa le variazioni negative dalle positive. ",
        "Un effetto di popolazione grande con un effetto di tasso piccolo significa che quello stato non si è svuotato per un cambiamento di comportamento, ma perché ci sono meno giovani."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, ", DA, " e ", A,
        ". Elaborazione: pipeline/edu (thread educazione), data/processed/edu_change_decomposition_2018_2024.csv (con edu_youth_states_2018_2024.csv per la coorte)."),
      larghezza = LARGHEZZA)
  ) +
  tema_figura() +
  theme(panel.spacing.x = unit(1.6, "lines"), panel.spacing.y = unit(1.1, "lines"))

salva(figura, "edu_fig04_scomposizione", larghezza = LARGHEZZA, altezza = 23)
