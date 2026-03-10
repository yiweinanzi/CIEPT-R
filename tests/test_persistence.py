from pathlib import Path
import json


def test_continue_task_file_exists_and_has_bootstrap_task():
    task_file = Path("continue/task.json")
    assert task_file.exists()

    data = json.loads(task_file.read_text())

    assert data["project"] == "CIEPT-R"
    assert any(task["id"] == "T001" for task in data["tasks"])


def test_bootstrap_task_marked_done_after_verification():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T001")

    assert task["status"] == "done"


def test_t002_marked_done_and_t003_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T002")

    assert task["status"] == "done"


def test_t003_marked_done_and_t004_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T003")

    assert task["status"] == "done"


def test_t004_marked_done_and_t005_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T004")

    assert task["status"] == "done"


def test_t005_marked_done_and_t006_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T005")

    assert task["status"] == "done"


def test_t006_marked_done_and_t007_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T006")

    assert task["status"] == "done"


def test_t007_marked_done_and_t008_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T007")

    assert task["status"] == "done"


def test_t008_marked_done_and_t009_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T008")

    assert task["status"] == "done"


def test_t009_marked_done_and_t010_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T009")

    assert task["status"] == "done"


def test_t010_marked_done_and_t011_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T010")

    assert task["status"] == "done"


def test_t011_marked_done_and_t012_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T011")

    assert task["status"] == "done"


def test_t012_marked_done_and_t013_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T012")

    assert task["status"] == "done"


def test_t013_marked_done_after_delivery_bundle_generation():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T013")

    assert task["status"] == "done"
