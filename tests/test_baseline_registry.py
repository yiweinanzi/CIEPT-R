from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.baselines.registry import build_baseline_inventory


def test_build_baseline_inventory_classifies_downloaded_and_missing_assets(tmp_path):
    (tmp_path / "LightGCN-master.zip").write_text("", encoding="utf-8")
    (tmp_path / "BM3-master.zip").write_text("", encoding="utf-8")
    (tmp_path / "DiffMM-main.zip").write_text("", encoding="utf-8")

    inventory = build_baseline_inventory(tmp_path)
    by_name = {entry["name"]: entry for entry in inventory}

    assert by_name["LightGCN"]["status"] == "direct_match"
    assert by_name["BM3"]["status"] == "direct_match"
    assert by_name["DiffMM"]["status"] == "mapped_candidate"
    assert by_name["RecGOAT"]["status"] == "missing"
