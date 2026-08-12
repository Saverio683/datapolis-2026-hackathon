# Rigenera tutte le figure in figures/. Da lanciare dalla radice: Rscript viz/build_all.R
# Prerequisito: notebooks/analisi.ipynb e notebooks/genere.ipynb già eseguiti.

VIZ <- if (dir.exists("viz")) "viz" else "."

for (script in list.files(VIZ, pattern = "^fig[0-9]+_.*\\.R$", full.names = TRUE)) {
  message("--- ", basename(script))
  # Ogni figura in un ambiente pulito: gli script non si passano stato fra loro.
  source(script, local = new.env())
}
