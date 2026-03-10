from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.config import load_config


def test_load_config_reads_project_name():
    config = load_config("configs/base.yaml")

    assert config["project"]["name"] == "CIEPT-R"
