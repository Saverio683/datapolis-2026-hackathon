from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
NOTEBOOK = ROOT / "notebooks" / "Bagheria_transizione_istruzione_lavoro.ipynb"


class PipelineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.quality = json.loads((PROCESSED / "quality_report.json").read_text(encoding="utf-8"))
        cls.validation = json.loads(
            (ROOT / "outputs" / "validation_report.json").read_text(encoding="utf-8")
        )
        cls.summary = json.loads((TABLES / "analysis_summary.json").read_text(encoding="utf-8"))
        cls.youth = pd.read_csv(TABLES / "youth_states_2018_2024.csv", dtype={"territorio": str})
        cls.gaps = pd.read_csv(TABLES / "gaps_vs_sicily.csv")
        cls.decomposition = pd.read_csv(TABLES / "change_decomposition_2018_2024.csv")

    def test_input_sentinels(self) -> None:
        checks = self.quality["checks"]
        self.assertEqual(checks["sicilian_municipalities_2011"], 390)
        self.assertEqual(checks["technical_schools_bagheria"], 3)
        self.assertEqual(checks["young_15_34_bagheria_2024"], 11861)

    def test_bagheria_2024_metrics(self) -> None:
        current = self.summary["current_2024"]
        self.assertTrue(np.isclose(current["population_15_24"], 5904))
        self.assertTrue(np.isclose(current["employed_count"], 734))
        self.assertTrue(np.isclose(current["inactive_nonstudent_pct"], 18.99345, atol=1e-4))
        self.assertTrue(np.isclose(current["inactive_share_of_outside_pct"], 70.57981, atol=1e-4))

    def test_youth_states_form_complete_composition(self) -> None:
        components = self.youth[
            ["quota_occupati", "quota_in_cerca", "quota_studenti", "quota_inattivi_non_studenti"]
        ]
        self.assertTrue(np.allclose(components.sum(axis=1), 100, atol=1e-8))
        self.assertTrue((components >= 0).all().all())

    def test_time_keys_are_explicit(self) -> None:
        self.assertNotIn(2020, set(self.youth["anno"]))
        self.assertFalse(self.youth.duplicated(["territorio", "anno"]).any())

    def test_employment_improves_without_convergence(self) -> None:
        series = self.gaps[
            (self.gaps["dominio"] == "giovani")
            & (self.gaps["metrica"] == "quota_occupati")
            & (self.gaps["anno"].isin([2018, 2024]))
        ].set_index("anno")
        self.assertGreater(self.summary["change_2018_2024"]["employment_pp"], 0)
        self.assertTrue(
            np.isclose(
                series.loc[2018, "gap_bagheria_sicilia_pp"],
                series.loc[2024, "gap_bagheria_sicilia_pp"],
                atol=0.01,
            )
        )

    def test_inactivity_is_persistent_relative_to_search(self) -> None:
        change = self.summary["change_2018_2024"]
        self.assertGreater(change["inactive_nonstudent_pp"], change["searching_pp"])
        self.assertLess(abs(change["inactive_nonstudent_pp"]), 1)
        self.assertGreater(self.summary["gaps_vs_sicily_2024"]["inactive_nonstudent_15_24_pp"], 4)

    def test_shift_share_identity_and_main_component(self) -> None:
        self.assertTrue(np.allclose(self.decomposition["check_decomposizione"], 0, atol=1e-8))
        states = self.decomposition[
            self.decomposition["metrica"].isin(
                ["occupati", "in_cerca", "studenti", "inattivi_non_studenti"]
            )
        ]
        changes = states.set_index("metrica")["variazione_conteggio"]
        self.assertEqual(changes.idxmin(), "in_cerca")

    def test_adult_education_and_employment_remain_below_sicily(self) -> None:
        gaps = self.summary["gaps_vs_sicily_2024"]
        self.assertLess(gaps["at_least_diploma_25_49_pp"], 0)
        self.assertLess(gaps["employment_25_49_pp"], 0)

    def test_peer_matching_does_not_use_outcomes(self) -> None:
        config = yaml.safe_load((ROOT / "config" / "analysis.yml").read_text(encoding="utf-8"))
        features = set(config["peer_matching"]["features"])
        excluded = set(config["peer_matching"]["excluded_outcomes"])
        self.assertTrue(features.isdisjoint(excluded))
        self.assertEqual(self.summary["peer_summary"]["n_peers"], 10)
        self.assertLess(self.summary["peer_summary"]["employment_gap_vs_peer_median"], 0)

    def test_models_are_appendix_only_and_exclude_bagheria(self) -> None:
        models = pd.read_csv(TABLES / "model_robustness_2011.csv")
        self.assertTrue((models["n_comuni_training"] == 389).all())
        self.assertTrue(models["uso"].str.contains("appendice", case=False).all())
        self.assertTrue((models.loc[models["outcome"] == "L14", "r2_cv_10fold"] < 0.1).all())

    def test_findings_are_five_supported_results(self) -> None:
        findings = pd.read_csv(TABLES / "finding_summary.csv")
        self.assertEqual(len(findings), 5)
        self.assertFalse(findings[["risultato", "evidenza", "implicazione", "forza"]].isna().any().any())

    def test_validation_report_is_green(self) -> None:
        self.assertEqual(self.validation["status"], "passed")
        self.assertEqual(self.validation["checks_passed"], self.validation["checks_total"])
        self.assertEqual(self.validation["checks_total"], 11)

    def test_final_narrative_has_no_old_idea_scaffolding(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / "outputs" / "REPORT_ANALITICO.md",
            ROOT / "outputs" / "EXECUTIVE_SUMMARY.md",
            ROOT / "outputs" / "POLICY_PONTE_19_BAGHERIA.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        forbidden = [r"talent trap", r"mestiere senza eredi", r"cinque ipotesi", r"divario di genere"]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, text, flags=re.IGNORECASE), pattern)

    def test_notebook_is_complete_and_executed(self) -> None:
        notebook = nbformat.read(NOTEBOOK, as_version=4)
        code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
        errors = [
            output
            for cell in code_cells
            for output in cell.get("outputs", [])
            if output.output_type == "error"
        ]
        images = sum(
            "data:image/png;base64" in output.get("data", {}).get("text/html", "")
            for cell in code_cells
            for output in cell.get("outputs", [])
        )
        self.assertGreaterEqual(len(code_cells), 20)
        self.assertTrue(all(cell.execution_count is not None for cell in code_cells))
        self.assertEqual(errors, [])
        self.assertEqual(images, 13)


if __name__ == "__main__":
    unittest.main()
