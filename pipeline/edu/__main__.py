"""Pipeline del thread educazione, dall'acquisizione ai report.

    uv run python -m pipeline.edu --skip-download   # dai raw già presenti
    uv run python -m pipeline.edu --refresh         # riscarica le fonti

Scrive le tavole edu_* in data/processed/, le figure in figures/edu/ e i
report (analitico, executive, policy, run/validation) in docs/analisi/educazione/.
"""
from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone

from .analysis import run_analysis
from .charts import build_all_charts
from .cleaning import build_clean_data
from .download import download_all
from .paths import OUTPUTS, ROOT, ensure_directories
from .policy import build_analytical_report, build_executive_summary, build_policy_report
from .validation import validate_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
LOGGER = logging.getLogger("datapolis.edu")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-download", action="store_true", help="usa i raw già presenti")
    parser.add_argument("--download-only", action="store_true", help="scarica senza elaborare")
    parser.add_argument("--refresh", action="store_true", help="riscarica anche le fonti presenti")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_directories()
    report: dict[str, object] = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(ROOT),
    }
    stage_times: dict[str, float] = {}

    def run_stage(name: str, function, *function_args, **function_kwargs):
        LOGGER.info("START %s", name)
        started = time.perf_counter()
        result = function(*function_args, **function_kwargs)
        stage_times[name] = round(time.perf_counter() - started, 3)
        LOGGER.info("DONE  %s (%.3fs)", name, stage_times[name])
        return result

    if not args.skip_download:
        report["download"] = run_stage("download", download_all, refresh=args.refresh)
    if args.download_only:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (OUTPUTS / "run_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return 0

    report["quality"] = run_stage("cleaning", build_clean_data)
    report["analysis"] = run_stage("analysis", run_analysis)
    report["validation"] = run_stage("validation", validate_pipeline)
    report["figures"] = [
        str(path.relative_to(ROOT)) for path in run_stage("charts", build_all_charts)
    ]
    policy = run_stage("policy", build_policy_report)
    report["policy"] = str(policy.splitlines()[0]).lstrip("# ")
    run_stage("analytical_report", build_analytical_report)
    run_stage("executive_summary", build_executive_summary)
    report["status"] = "passed"
    report["stage_seconds"] = stage_times
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (OUTPUTS / "run_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
