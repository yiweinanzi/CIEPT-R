from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile


@dataclass(frozen=True)
class ExtractedBaselineArchive:
    archive_path: Path
    extraction_root: Path
    extracted_dir: Path
    root_name: str


def _detect_root_name(members: list[str]) -> str:
    roots = {Path(member).parts[0] for member in members if member}
    if len(roots) != 1:
        raise ValueError("Archive must contain a single top-level root directory")
    return next(iter(roots))


def extract_baseline_archive(archive_path: Path, extraction_root: Path) -> ExtractedBaselineArchive:
    archive_path = Path(archive_path)
    extraction_root = Path(extraction_root)
    extraction_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path) as zf:
        root_name = _detect_root_name(zf.namelist())
        extracted_dir = extraction_root / root_name
        if not extracted_dir.exists():
            zf.extractall(extraction_root)

    return ExtractedBaselineArchive(
        archive_path=archive_path,
        extraction_root=extraction_root,
        extracted_dir=extracted_dir,
        root_name=root_name,
    )
