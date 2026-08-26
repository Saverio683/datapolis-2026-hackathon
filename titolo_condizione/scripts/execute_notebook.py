#!/usr/bin/env python3
"""Esegue un notebook nello stesso processo, utile in sandbox senza socket locali."""

from __future__ import annotations

import argparse
import base64
import contextlib
import html as html_module
import io
import os
import traceback
from pathlib import Path

import nbformat
import pandas as pd
from IPython.display import HTML, Image, Markdown


def _display_output(value: object) -> dict:
    if isinstance(value, pd.DataFrame):
        return nbformat.v4.new_output(
            "display_data",
            data={"text/html": value.to_html(), "text/plain": repr(value)},
            metadata={},
        )
    if isinstance(value, Markdown):
        source = str(value.data)
        return nbformat.v4.new_output(
            "display_data",
            data={"text/markdown": source, "text/plain": source},
            metadata={},
        )
    if isinstance(value, HTML):
        source = str(value.data)
        return nbformat.v4.new_output(
            "display_data",
            data={"text/html": source, "text/plain": source},
            metadata={},
        )
    if isinstance(value, Image):
        binary = value.data
        if isinstance(binary, str):
            binary = binary.encode("utf-8")
        encoded = base64.b64encode(binary).decode("ascii")
        alt = html_module.escape(value.alt or "Grafico dell'analisi")
        markup = (
            f'<img src="data:{value._mimetype};base64,{encoded}" alt="{alt}" '
            'style="max-width:100%;height:auto"/>'
        )
        return nbformat.v4.new_output(
            "display_data",
            data={"text/html": markup, "text/plain": value.alt or "Grafico dell'analisi"},
            metadata={},
        )
    html_repr = getattr(value, "_repr_html_", None)
    if callable(html_repr):
        html = html_repr()
        if html is not None:
            return nbformat.v4.new_output(
                "display_data",
                data={"text/html": html, "text/plain": repr(value)},
                metadata={},
            )
    return nbformat.v4.new_output(
        "display_data", data={"text/plain": repr(value)}, metadata={}
    )


def execute(path: Path, workdir: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    namespace: dict[str, object] = {"__name__": "__main__"}
    previous = Path.cwd()
    os.chdir(workdir)
    try:
        execution_count = 0
        for cell_number, cell in enumerate(notebook.cells, start=1):
            if cell.cell_type != "code":
                continue
            execution_count += 1
            outputs: list[dict] = []
            stdout = io.StringIO()
            stderr = io.StringIO()

            def captured_display(*values: object, **_: object) -> None:
                outputs.extend(_display_output(value) for value in values)

            namespace["display"] = captured_display
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exec(compile(cell.source, f"{path.name}:cell-{cell_number}", "exec"), namespace)
                namespace["display"] = captured_display
            except Exception as exc:
                outputs.append(
                    nbformat.v4.new_output(
                        "error",
                        ename=type(exc).__name__,
                        evalue=str(exc),
                        traceback=traceback.format_exc().splitlines(),
                    )
                )
                cell.outputs = outputs
                cell.execution_count = execution_count
                nbformat.write(notebook, path)
                raise

            if stdout.getvalue():
                outputs.insert(0, nbformat.v4.new_output("stream", name="stdout", text=stdout.getvalue()))
            if stderr.getvalue():
                outputs.append(nbformat.v4.new_output("stream", name="stderr", text=stderr.getvalue()))
            cell.outputs = outputs
            cell.execution_count = execution_count
    finally:
        os.chdir(previous)
    notebook.metadata["execution"] = {
        "engine": "in-process",
        "reason": "compatibile con ambienti sandbox senza socket TCP locali",
    }
    nbformat.write(notebook, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--workdir", type=Path, default=Path.cwd())
    args = parser.parse_args()
    execute(args.notebook.resolve(), args.workdir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
