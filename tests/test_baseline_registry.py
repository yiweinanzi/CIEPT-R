from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.baselines.registry import build_baseline_inventory


def test_build_baseline_inventory_classifies_downloaded_and_missing_assets(tmp_path):
    (tmp_path / "LightGCN-master.zip").write_text("", encoding="utf-8")
    (tmp_path / "BM3-master.zip").write_text("", encoding="utf-8")
    (tmp_path / "CLEAR-replication-main.zip").write_text("", encoding="utf-8")
    (tmp_path / "Guider-main.zip").write_text("", encoding="utf-8")
    (tmp_path / "MAGNET-main.zip").write_text("", encoding="utf-8")
    (tmp_path / "DiffMM-main.zip").write_text("", encoding="utf-8")
    (tmp_path / "SMORE-main.zip").write_text("", encoding="utf-8")
    (tmp_path / "MixRec-main.zip").write_text("", encoding="utf-8")

    inventory = build_baseline_inventory(tmp_path)
    by_name = {entry["name"]: entry for entry in inventory}

    assert by_name["LightGCN"]["status"] == "direct_match"
    assert by_name["LightGCN"]["dataset_format"] == "recbole"
    assert by_name["BM3"]["status"] == "direct_match"
    assert by_name["BM3"]["integration_mode"] == "mmrec"
    assert by_name["DiffMM"]["status"] == "mapped_candidate"
    assert by_name["DiffMM"]["main_table"] is False
    assert by_name["DiffMM"]["integration_mode"] == "diffmm"
    assert by_name["Guider"]["status"] == "mapped_match"
    assert by_name["Guider"]["paper_mapping"] == "Teach Me How to Denoise"
    assert by_name["Guider"]["integration_mode"] == "guided_mmrec"
    assert by_name["MAGNET"]["status"] == "asset_incomplete"
    assert by_name["MAGNET"]["paper_mapping"] == "Modality-Guided Mixture of Graph Experts"
    assert by_name["MAGNET"]["integration_mode"] == "asset_incomplete"
    assert by_name["SMORE"]["status"] == "mapped_candidate"
    assert by_name["SMORE"]["integration_mode"] == "mmrec"
    assert by_name["MixRec"]["status"] == "runtime_mismatch"
    assert by_name["MixRec"]["next_action"] == "Keep blocked unless a compatible single-behavior runner is introduced."
    assert by_name["CLEAR"]["status"] == "asset_mismatch"
    assert by_name["CLEAR"]["next_action"] == "Acquire the multimodal CLEAR baseline implementation."
    assert by_name["RecGOAT"]["status"] == "missing"
    assert by_name["IGDMRec"]["status"] == "missing"
