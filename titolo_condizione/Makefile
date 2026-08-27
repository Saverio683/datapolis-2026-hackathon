.PHONY: all download process notebook test clean

all:
	uv run python scripts/run_pipeline.py
	uv run python scripts/build_notebook.py
	uv run python scripts/execute_notebook.py notebooks/Bagheria_transizione_istruzione_lavoro.ipynb --workdir .
	uv run python -m nbconvert --to html notebooks/Bagheria_transizione_istruzione_lavoro.ipynb --output-dir notebooks --output Bagheria_transizione_istruzione_lavoro.html

download:
	uv run python scripts/run_pipeline.py --download-only --refresh

process:
	uv run python scripts/run_pipeline.py --skip-download

notebook:
	uv run python scripts/build_notebook.py
	uv run python scripts/execute_notebook.py notebooks/Bagheria_transizione_istruzione_lavoro.ipynb --workdir .
	uv run python -m nbconvert --to html notebooks/Bagheria_transizione_istruzione_lavoro.ipynb --output-dir notebooks --output Bagheria_transizione_istruzione_lavoro.html

test:
	uv run python -m unittest discover -s tests -v

clean:
	find data/interim data/processed outputs/figures outputs/tables -type f -delete
