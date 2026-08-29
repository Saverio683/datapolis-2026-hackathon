# Rigenera tutte le figure in figures/. Da lanciare dalla radice: Rscript viz/build_all.R
# Prerequisito: notebooks/analisi.ipynb, genere.ipynb e mobilita.ipynb già eseguiti.

VIZ <- if (dir.exists("viz")) "viz" else "."

# Il suffisso di lettera è lo scorporo: fig06 e fig06b nascono dalla stessa domanda ma
# sono due figure autonome. La lettera tiene la parentela visibile e l'ordine giusto.
# I prefissi `edu_` e `mob_` sono le numerazioni dei thread educazione e mobilità,
# separate da quella del thread genere: le due serie hanno figure diverse con lo stesso numero, e mescolarle nello
# stesso spazio di nomi vorrebbe dire rinumerare una delle due a ogni aggiunta.
for (script in list.files(VIZ, pattern = "^(edu_|mob_)?fig[0-9]+[a-z]?_.*\\.R$",
                          full.names = TRUE)) {
  message("--- ", basename(script))
  # Ogni figura in un ambiente pulito: gli script non si passano stato fra loro.
  source(script, local = new.env())
}
