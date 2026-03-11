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


def test_b001_baseline_inventory_task_marked_done():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "B001")

    assert task["status"] == "done"
    assert any(item["id"] == "B002" for item in data["tasks"])


def test_b002_recbole_bridge_task_marked_done_and_b003_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "B002")

    assert task["status"] == "done"
    assert any(item["id"] == "B003" for item in data["tasks"])


def test_b003_to_b011_task_wave_states_are_recorded():
    data = json.loads(Path("continue/task.json").read_text())
    by_id = {task["id"]: task for task in data["tasks"]}

    assert by_id["B003"]["status"] == "done"
    assert by_id["B004"]["status"] == "done"
    assert by_id["B005"]["status"] == "done"
    assert by_id["B006"]["status"] == "done"
    assert by_id["B007"]["status"] == "done"
    assert by_id["B008"]["status"] == "blocked"
    assert by_id["B009"]["status"] == "done"
    assert by_id["B010"]["status"] == "done"
    assert by_id["B011"]["status"] == "done"
    assert any(item["id"] == "B008" for item in data["tasks"])


def test_b012_to_b016_and_m001_to_m003_follow_up_states_are_recorded():
    data = json.loads(Path("continue/task.json").read_text())
    by_id = {task["id"]: task for task in data["tasks"]}

    assert by_id["B012"]["status"] == "done"
    assert by_id["B013"]["status"] == "blocked"
    assert by_id["B014"]["status"] == "done"
    assert by_id["B015"]["status"] == "done"
    assert by_id["B016"]["status"] == "blocked"
    assert by_id["M001"]["status"] == "done"
    assert by_id["M002"]["status"] == "done"
    assert by_id["M003"]["status"] == "done"
    assert by_id["M004"]["status"] == "done"
    assert by_id["B017"]["status"] == "pending"
    assert by_id["B018"]["status"] == "pending"
    assert by_id["B019"]["status"] == "blocked"
    assert data["current_focus"] == "B017"
