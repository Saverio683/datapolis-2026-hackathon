from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .paths import OUTPUTS, PROCESSED, RAW, TABLES


def _check(name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def _verify_latest_hashes() -> tuple[bool, str]:
    manifest = pd.read_csv(RAW / "manifest.csv")
    latest = manifest.sort_values("checked_at_utc").groupby("source_id", as_index=False).tail(1)
    verified = 0
    failures: list[str] = []
    for row in latest.itertuples():
        if row.status != "downloaded":
            continue
        path = RAW / row.file
        if not path.exists():
            failures.append(f"{row.source_id}: file assente")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row.sha256:
            failures.append(f"{row.source_id}: SHA-256 diverso")
        else:
            verified += 1
    return not failures, f"{verified} raw verificati" + (f"; {failures}" if failures else "")


def validate_pipeline() -> dict[str, object]:
    checks: list[dict[str, object]] = []
    hash_ok, hash_detail = _verify_latest_hashes()
    checks.append(_check("raw_sha256", hash_ok, hash_detail))

    quality = json.loads((PROCESSED / "edu_quality_report.json").read_text(encoding="utf-8"))
    checks.append(_check(
        "municipalities_2011",
        quality["checks"]["sicilian_municipalities_2011"] == 390,
        f"osservati {quality['checks']['sicilian_municipalities_2011']} comuni",
    ))

    youth = pd.read_csv(TABLES / "edu_youth_states_2018_2024.csv", dtype={"territorio": str})
    composition = youth[[
        "quota_occupati", "quota_in_cerca", "quota_studenti", "quota_inattivi_non_studenti"
    ]].sum(axis=1)
    checks.append(_check(
        "youth_composition_100",
        bool(np.allclose(composition, 100, atol=0.05)),
        f"deviazione massima {float((composition - 100).abs().max()):.6f} p.p.",
    ))
    checks.append(_check(
        "no_work_2020_interpolation",
        2020 not in set(youth["anno"]),
        f"anni presenti {sorted(map(int, youth['anno'].unique()))}",
    ))
    checks.append(_check(
        "unique_youth_keys",
        not youth.duplicated(["territorio", "anno"]).any(),
        f"duplicati {int(youth.duplicated(['territorio', 'anno']).sum())}",
    ))
    checks.append(_check(
        "nonnegative_youth_values",
        bool((youth.select_dtypes(include="number") >= -1e-9).all().all()),
        "conteggi e quote non negativi",
    ))

    bagheria_2024 = youth[(youth["territorio"].eq("082006")) & (youth["anno"].eq(2024))]
    sentinel_ok = len(bagheria_2024) == 1 and np.isclose(bagheria_2024.iloc[0]["occupati"], 734)
    checks.append(_check("sentinel_bagheria_2024", sentinel_ok, "occupati 15-24 attesi: 734"))

    decomposition = pd.read_csv(TABLES / "edu_change_decomposition_2018_2024.csv")
    checks.append(_check(
        "shift_share_identity",
        bool(np.allclose(decomposition["check_decomposizione"], 0, atol=1e-7)),
        f"residuo massimo {float(decomposition['check_decomposizione'].abs().max()):.3e}",
    ))

    inventory = pd.read_csv(TABLES / "edu_source_inventory.csv")
    core = inventory[inventory["ruolo"].eq("core")]
    checks.append(_check(
        "core_sources_available",
        core["stato"].eq("available").all(),
        ", ".join(f"{row.dataset}: {row.stato}" for row in core.itertuples()),
    ))

    robustness = pd.read_csv(TABLES / "edu_model_robustness_2011.csv")
    checks.append(_check(
        "bagheria_out_of_training",
        bool((robustness["n_comuni_training"] == 389).all()),
        f"n training: {sorted(robustness['n_comuni_training'].unique())}",
    ))

    findings = pd.read_csv(TABLES / "edu_finding_summary.csv")
    checks.append(_check(
        "findings_are_supported",
        len(findings) == 5 and findings["evidenza"].notna().all(),
        f"{len(findings)} risultati con evidenza esplicita",
    ))

    errors = [item for item in checks if not item["passed"]]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not errors else "failed",
        "checks_passed": len(checks) - len(errors),
        "checks_total": len(checks),
        "checks": checks,
    }
    (OUTPUTS / "validation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        raise AssertionError("validazione fallita: " + "; ".join(str(item) for item in errors))
    return report
