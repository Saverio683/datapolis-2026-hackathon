from __future__ import annotations

import csv
import hashlib
import io
import json
import time
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .paths import CONFIG, RAW, ensure_directories


SDMX_BASE = "https://esploradati.istat.it/SDMXWS/rest"
SDMX_ACCEPT = "application/vnd.sdmx.data+csv;version=1.0.0"
TERRITORIES = "082006+082053+ITG1+IT"
MIUR_ENDPOINT = "https://dati.istruzione.it/opendata/SCUANAGRAFESTAT/query"
MANIFEST = RAW / "manifest.csv"


@dataclass(frozen=True)
class Source:
    id: str
    provider: str
    extension: str
    required: bool
    expected_marker: str
    license: str
    purpose: str
    url: str | None = None
    dataflow: str | None = None
    dimensions: int | None = None
    kind: str | None = None


def load_sources() -> list[Source]:
    content = yaml.safe_load((CONFIG / "sources.yml").read_text(encoding="utf-8"))
    return [Source(**item) for item in content["sources"]]


def _session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "DataPolis-Bagheria/1.0", "Accept-Language": "it"})
    return session


def _sdmx_url(dataflow: str, dimensions: int) -> str:
    key = ".".join(["A", TERRITORIES] + [""] * (dimensions - 2))
    return f"{SDMX_BASE}/data/IT1,{dataflow},1.0/{key}/ALL/?detail=full"


def _request_spec(source: Source) -> tuple[str, dict[str, str], dict[str, str] | None]:
    headers: dict[str, str] = {}
    params: dict[str, str] | None = None
    if source.dataflow:
        if not source.dimensions:
            raise ValueError(f"dimensioni SDMX mancanti per {source.id}")
        headers["Accept"] = SDMX_ACCEPT
        return _sdmx_url(source.dataflow, source.dimensions), headers, None
    if source.kind == "miur_sparql":
        query = (CONFIG / "technical_schools.sparql").read_text(encoding="utf-8")
        params = {"query": query, "dataType": "csv"}
        return MIUR_ENDPOINT, headers, params
    if not source.url:
        raise ValueError(f"URL mancante per {source.id}")
    return source.url, headers, params


def _validate_blob(source: Source, blob: bytes) -> None:
    if source.extension == "zip":
        if not zipfile.is_zipfile(io.BytesIO(blob)):
            raise ValueError("la risposta non è un archivio ZIP valido")
        return
    if source.expected_marker:
        first_line = blob.splitlines()[0] if blob else b""
        marker = source.expected_marker.encode("utf-8")
        if marker not in first_line and marker not in first_line.decode("cp1252", errors="ignore").encode("utf-8"):
            raise ValueError(f"marcatore {source.expected_marker!r} assente nella prima riga")


def _latest_successes() -> set[str]:
    if not MANIFEST.exists():
        return set()
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        return {row["file"] for row in csv.DictReader(handle) if row.get("status") == "downloaded"}


def _append_manifest(row: dict[str, Any]) -> None:
    fields = [
        "checked_at_utc", "source_id", "provider", "file", "url", "status",
        "required", "bytes", "sha256", "license", "purpose", "message",
    ]
    exists = MANIFEST.exists()
    with MANIFEST.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in fields})


def download_all(refresh: bool = False) -> dict[str, Any]:
    """Scarica tutte le fonti e registra anche le indisponibilità delle fonti opzionali."""
    ensure_directories()
    session = _session()
    today = date.today().isoformat()
    existing = _latest_successes()
    results: list[dict[str, Any]] = []
    required_errors: list[str] = []

    for source in load_sources():
        filename = f"{source.id}_{today}.{source.extension}"
        destination = RAW / filename
        url, headers, params = _request_spec(source)
        if destination.exists() and filename in existing and not refresh:
            results.append({"source_id": source.id, "status": "cached", "file": filename})
            continue

        checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            response = session.get(url, headers=headers, params=params, timeout=180)
            response.raise_for_status()
            blob = response.content
            _validate_blob(source, blob)
            destination.write_bytes(blob)
            digest = hashlib.sha256(blob).hexdigest()
            row = {
                "checked_at_utc": checked_at,
                "source_id": source.id,
                "provider": source.provider,
                "file": filename,
                "url": response.url,
                "status": "downloaded",
                "required": source.required,
                "bytes": len(blob),
                "sha256": digest,
                "license": source.license,
                "purpose": source.purpose,
                "message": "",
            }
            _append_manifest(row)
            results.append(row)
        except Exception as exc:  # l'esito negativo è parte dell'audit delle fonti
            message = f"{type(exc).__name__}: {exc}"
            row = {
                "checked_at_utc": checked_at,
                "source_id": source.id,
                "provider": source.provider,
                "file": filename,
                "url": url,
                "status": "unavailable",
                "required": source.required,
                "bytes": 0,
                "sha256": "",
                "license": source.license,
                "purpose": source.purpose,
                "message": message[:500],
            }
            _append_manifest(row)
            results.append(row)
            if source.required:
                required_errors.append(f"{source.id}: {message}")
        time.sleep(0.15)

    status = {row["source_id"]: row["status"] for row in results}
    (RAW / "download_status.json").write_text(
        json.dumps({"generated_at_utc": datetime.now(timezone.utc).isoformat(), "sources": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if required_errors:
        raise RuntimeError("fonti obbligatorie indisponibili:\n" + "\n".join(required_errors))
    return {"status": status, "results": results}


def latest_raw(source_id: str, extension: str | None = None) -> Path:
    suffix = f".{extension}" if extension else ".*"
    candidates = sorted(RAW.glob(f"{source_id}_*{suffix}"))
    if not candidates:
        raise FileNotFoundError(f"nessun raw disponibile per {source_id}")
    return candidates[-1]

