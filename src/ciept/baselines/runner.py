from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import textwrap
from typing import Callable

from ciept.baselines.archive import extract_baseline_archive
from ciept.baselines.data_bridge import bridge_presplit_dataset_to_recbole
from ciept.baselines.formats import (
    PreparedBaselineDataset,
    prepare_diffmm_dataset,
    prepare_graph_imputation_dataset,
    prepare_i3mrec_dataset,
    prepare_mmrec_dataset,
    prepare_vbpr_dataset,
)
from ciept.baselines.recbole_adapter import build_recbole_config, is_recbole_available
from ciept.baselines.registry import build_baseline_inventory


BaselineExecutor = Callable[[dict, PreparedBaselineDataset, Path], dict]


@dataclass(frozen=True)
class BaselineRunRequest:
    baseline_name: str
    dataset_name: str
    source_dir: Path
    baselines_dir: Path
    results_root: Path
    run_id: str


@dataclass(frozen=True)
class BaselineRunResult:
    baseline_name: str
    dataset_name: str
    integration_mode: str
    run_id: str
    run_dir: Path
    metrics: dict[str, float]
    notes: list[str]


def _get_baseline_record(baseline_name: str, baselines_dir: Path) -> dict:
    inventory = build_baseline_inventory(baselines_dir)
    for record in inventory:
        if record["name"] == baseline_name:
            return record
    raise ValueError(f"Unknown baseline: {baseline_name}")


def _prepare_run_directory(results_root: Path, baseline_name: str, run_id: str) -> Path:
    run_dir = Path(results_root) / "baselines" / baseline_name / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _normalize_executor_output(payload: dict) -> tuple[dict[str, float], list[str]]:
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("Baseline executor must return a non-empty 'metrics' mapping")

    notes = payload.get("notes", [])
    if not isinstance(notes, list):
        raise ValueError("Baseline executor 'notes' must be a list of strings")

    normalized_metrics = {str(key): float(value) for key, value in metrics.items()}
    normalized_notes = [str(note) for note in notes]
    return normalized_metrics, normalized_notes


def _write_run_outputs(result: BaselineRunResult) -> None:
    metrics_path = result.run_dir / "metrics.json"
    summary_path = result.run_dir / "summary.md"

    metrics_path.write_text(
        json.dumps(
            {
                "baseline_name": result.baseline_name,
                "dataset_name": result.dataset_name,
                "integration_mode": result.integration_mode,
                "run_id": result.run_id,
                "metrics": result.metrics,
                "notes": result.notes,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    summary_path.write_text(
        "\n".join(
            [
                f"# {result.baseline_name}",
                "",
                f"- dataset: {result.dataset_name}",
                f"- run_id: {result.run_id}",
                f"- integration_mode: {result.integration_mode}",
                "",
                "## Metrics",
                *[f"- {name}: {value}" for name, value in result.metrics.items()],
                "",
                "## Notes",
                *[f"- {note}" for note in result.notes],
            ]
        ),
        encoding="utf-8",
    )


def _prepare_recbole_dataset(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
    baseline_name: str,
) -> PreparedBaselineDataset:
    dataset_dir = Path(output_dir) / dataset_name
    bridge = bridge_presplit_dataset_to_recbole(dataset_name=dataset_name, source_dir=source_dir, output_dir=dataset_dir)
    config = build_recbole_config(
        dataset_name=dataset_name,
        data_path=bridge.output_dir.parent,
        model_name=baseline_name,
        benchmark_filename=bridge.benchmark_filename,
    )
    metadata = {
        "benchmark_filename": bridge.benchmark_filename,
        "recbole_config": config,
    }
    return PreparedBaselineDataset(
        dataset_name=dataset_name,
        dataset_format="recbole",
        source_dir=Path(source_dir),
        output_dir=bridge.output_dir,
        manifest_path=bridge.manifest_path,
        metadata=metadata | {"item_count": _count_atomic_records(bridge.output_dir / f"{dataset_name}.train.inter")},
    )


def _count_atomic_records(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    item_ids = {line.split("\t")[1] for line in lines[1:] if "\t" in line}
    return len(item_ids)


def _run_python_snippet(snippet: str, cwd: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, "-u", "-c", snippet],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in reversed(completed.stdout.splitlines()):
        if line.startswith("JSON_RESULT="):
            return json.loads(line.removeprefix("JSON_RESULT="))
    raise RuntimeError(f"Executor did not emit JSON_RESULT marker. stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")


def _default_recbole_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    if not is_recbole_available():
        raise RuntimeError(
            "RecBole is not installed. Install recbole or provide an executor override for testing."
        )
    from recbole.quick_start import run_recbole

    item_count = max(int(prepared.metadata.get("item_count", 3)), 2)
    topk = min(2, item_count - 1 if item_count > 1 else 1)
    config = dict(prepared.metadata["recbole_config"])
    config.update(
        {
            "epochs": 1,
            "train_batch_size": 8,
            "eval_batch_size": 8,
            "stopping_step": 1,
            "show_progress": False,
            "save_dataset": False,
            "save_dataloaders": False,
            "checkpoint_dir": str(run_dir / "checkpoints"),
            "gpu_id": -1,
            "use_gpu": False,
            "metrics": ["Recall", "NDCG"],
            "topk": [topk],
            "valid_metric": f"Recall@{topk}",
            "state": "ERROR",
            "seed": 0,
            "reproducibility": True,
        }
    )
    result = run_recbole(model=record["name"], dataset=prepared.dataset_name, config_dict=config, saved=False)
    return {
        "metrics": {key.upper(): value for key, value in result["test_result"].items()},
        "notes": ["Executed the RecBole smoke path on the prepared presplit dataset."],
    }


def _default_vbpr_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    repo_dir = Path(str(prepared.metadata["repo_dir"]))
    snippet = textwrap.dedent(
        f"""
        import json
        from pathlib import Path
        import numpy as np
        import pandas as pd
        import torch
        import sys

        sys.path.insert(0, {json.dumps(str(repo_dir))})
        from vbpr import VBPR

        prepared_dir = Path({json.dumps(str(prepared.output_dir))})
        df = pd.read_csv(prepared_dir / "interactions.csv")
        features = torch.tensor(np.load(prepared_dir / "visual_features.npy"), dtype=torch.float32)
        train_df = df[df["split"] == "train"]
        valid_df = df[df["split"] == "valid"]
        test_df = df[df["split"] == "test"]
        all_user_items = df.groupby("user_idx")["item_idx"].apply(set).to_dict()
        train_user_items = train_df.groupby("user_idx")["item_idx"].apply(set).to_dict()
        num_users = int(df["user_idx"].max()) + 1
        num_items = int(df["item_idx"].max()) + 1
        model = VBPR(num_users, num_items, features, dim_gamma=4, dim_theta=4)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
        rng = np.random.default_rng(0)

        for row in train_df.itertuples(index=False):
            uid = int(row.user_idx)
            pos = int(row.item_idx)
            neg = int(rng.integers(num_items))
            while neg in train_user_items.get(uid, set()):
                neg = int(rng.integers(num_items))
            u = torch.tensor([uid], dtype=torch.long)
            i = torch.tensor([pos], dtype=torch.long)
            j = torch.tensor([neg], dtype=torch.long)
            optimizer.zero_grad()
            score = model(u, i, j)
            loss = -torch.nn.functional.logsigmoid(score).mean()
            loss.backward()
            optimizer.step()

        def auc(eval_df):
            wins = []
            for row in eval_df.itertuples(index=False):
                uid = int(row.user_idx)
                pos = int(row.item_idx)
                neg = int(rng.integers(num_items))
                while neg in all_user_items.get(uid, set()):
                    neg = int(rng.integers(num_items))
                diff = model(torch.tensor([uid]), torch.tensor([pos]), torch.tensor([neg]))
                wins.append(float(diff.item() > 0))
            return sum(wins) / len(wins) if len(wins) else 0.0

        print("JSON_RESULT=" + json.dumps({{
            "metrics": {{
                "VALID_AUC": auc(valid_df),
                "TEST_AUC": auc(test_df),
            }},
            "notes": ["Executed the upstream VBPR model on the prepared presplit dataset."],
        }}, sort_keys=True))
        """
    )
    return _run_python_snippet(snippet, cwd=run_dir)


def _default_mmrec_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    repo_dir = Path(str(prepared.metadata["repo_dir"]))
    repo_entry_dir = Path(str(prepared.metadata.get("repo_entry_dir", repo_dir)))
    use_scatter_stub = record["name"] in {"MGCN", "SMORE"}
    snippet = textwrap.dedent(
        f"""
        import json
        from pathlib import Path
        import os
        import sys
        import types
        import numpy as np
        import torch
        import torch.nn as nn

        np.float = float
        np.int = int
        torch.Tensor.cuda = lambda self, *args, **kwargs: self
        nn.Module.cuda = lambda self, *args, **kwargs: self

        class _Identity:
            def __init__(self, *args, **kwargs):
                pass
            def __call__(self, value, *args, **kwargs):
                return value

        def _compose(steps):
            def _apply(value):
                for step in steps:
                    value = step(value)
                return value
            return _apply

        functional = types.SimpleNamespace(pad=lambda img,*a,**k: img, resize=lambda img,*a,**k: img)
        transforms_mod = types.SimpleNamespace(Compose=_compose, Resize=_Identity, Pad=_Identity, ToTensor=_Identity, functional=functional)
        sys.modules["torchvision"] = types.SimpleNamespace(transforms=transforms_mod)
        sys.modules["torchvision.transforms"] = transforms_mod
        sys.modules["torchvision.transforms.functional"] = functional

        if {repr(use_scatter_stub)}:
            def scatter_add(src, index, dim=0, dim_size=None):
                if dim != 0:
                    raise NotImplementedError
                if dim_size is None:
                    dim_size = int(index.max().item()) + 1 if index.numel() else 0
                out = torch.zeros(dim_size, dtype=src.dtype, device=src.device)
                out.scatter_add_(0, index, src)
                return out
            sys.modules["torch_scatter"] = types.SimpleNamespace(scatter_add=scatter_add)

        repo_dir = Path({json.dumps(str(repo_dir))})
        repo_entry_dir = Path({json.dumps(str(repo_entry_dir))})
        prepared_dir = Path({json.dumps(str(prepared.output_dir))})
        for package_name in ["models", "utils", "common"]:
            package_dir = repo_entry_dir / package_name
            if package_dir.exists():
                (package_dir / "__init__.py").touch(exist_ok=True)
        os.chdir(repo_entry_dir)
        sys.path.insert(0, str(repo_entry_dir))

        from utils.configurator import Config
        from utils.dataset import RecDataset
        from utils.dataloader import TrainDataLoader, EvalDataLoader
        from utils.utils import init_seed, get_model, get_trainer

        config_dict = {{
            "model": {json.dumps(record["name"])},
            "dataset": prepared_dir.name,
            "data_path": str(prepared_dir.parent) + "/",
            "inter_file_name": {json.dumps(str(prepared.metadata["inter_file_name"]))},
            "vision_feature_file": {json.dumps(str(prepared.metadata["image_feature_file"]))},
            "text_feature_file": {json.dumps(str(prepared.metadata["text_feature_file"]))},
            "field_separator": "\\t",
            "USER_ID_FIELD": "userID",
            "ITEM_ID_FIELD": "itemID",
            "TIME_FIELD": "timestamp",
            "inter_splitting_label": "x_label",
            "filter_out_cod_start_users": True,
            "gpu_id": 0,
            "use_gpu": False,
            "seed": [0],
            "epochs": 1,
            "stopping_step": 1,
            "train_batch_size": 2,
            "eval_batch_size": 2,
            "metrics": ["Recall", "NDCG"],
            "topk": [2],
            "valid_metric": "Recall@2",
            "hyper_parameters": ["seed"],
            "save_recommended_topk": False,
            "n_layers": 1,
        }}
        if {json.dumps(record["name"])} == "BM3":
            config_dict.update({{"dropout": 0.3, "reg_weight": 0.1}})
        if {json.dumps(record["name"])} == "MGCN":
            config_dict.update({{"n_ui_layers": 1, "cl_loss": 0.001, "knn_k": 1, "reg_weight": 1e-4}})
        if {json.dumps(record["name"])} == "SMORE":
            config_dict.update({{"n_ui_layers": 1, "image_knn_k": 1, "text_knn_k": 1, "dropout_rate": 0.1, "reg_weight": 1e-4, "cl_loss": 0.01}})
        if {json.dumps(record["name"])} == "MAGNET":
            config_dict.update({{"n_ui_layers": 1, "num_experts": 3, "topk_experts": 1, "reg_weight": 1e-4}})

        config = Config({json.dumps(record["name"])}, prepared_dir.name, config_dict)
        init_seed(0)
        dataset = RecDataset(config)
        str(dataset)
        train_dataset, valid_dataset, test_dataset = dataset.split()
        str(train_dataset); str(valid_dataset); str(test_dataset)
        train_data = TrainDataLoader(config, train_dataset, batch_size=config["train_batch_size"], shuffle=True)
        valid_data = EvalDataLoader(config, valid_dataset, additional_dataset=train_dataset, batch_size=config["eval_batch_size"])
        test_data = EvalDataLoader(config, test_dataset, additional_dataset=train_dataset, batch_size=config["eval_batch_size"])
        model = get_model(config["model"])(config, train_data).to(config["device"])
        trainer = get_trainer()(config, model)
        best_valid_score, best_valid_result, best_test_upon_valid = trainer.fit(train_data, valid_data=valid_data, test_data=test_data, saved=False)
        print("JSON_RESULT=" + json.dumps({{
            "metrics": {{
                "BEST_VALID_SCORE": float(best_valid_score),
                **{{key.upper(): value for key, value in best_test_upon_valid.items()}},
            }},
            "notes": ["Executed the upstream MMRec-style smoke path on the prepared presplit dataset."],
        }}, sort_keys=True))
        """
    )
    return _run_python_snippet(snippet, cwd=run_dir)


def _default_i3mrec_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    repo_dir = Path(str(prepared.metadata["repo_dir"]))
    snippet = textwrap.dedent(
        f"""
        import json
        from pathlib import Path
        import os
        import runpy
        import shutil
        import sys
        import types
        import numpy as np
        import torch
        import torch.nn as nn

        torch.Tensor.cuda = lambda self, *args, **kwargs: self
        nn.Module.cuda = lambda self, *args, **kwargs: self

        class IndexFlatIP:
            def __init__(self, dim):
                self.matrix = None
            def add(self, item_matrix):
                self.matrix = np.asarray(item_matrix)
            def search(self, query_vectors, k):
                query = np.asarray(query_vectors)
                scores = query @ self.matrix.T
                top_idx = np.argsort(-scores, axis=1)[:, :k]
                top_scores = np.take_along_axis(scores, top_idx, axis=1)
                return top_scores, top_idx

        numba_stub = types.SimpleNamespace(
            njit=lambda *args, **kwargs: (lambda fn: fn),
            typed=types.SimpleNamespace(List=lambda x: x),
        )
        sys.modules["faiss"] = types.SimpleNamespace(IndexFlatIP=IndexFlatIP)
        sys.modules["numba"] = numba_stub
        sys.modules["numba"].prange = range

        repo_dir = Path({json.dumps(str(repo_dir))})
        prepared_dir = Path({json.dumps(str(prepared.output_dir))})
        data_dir = repo_dir / "Data" / {json.dumps(prepared.dataset_name)}
        data_dir.mkdir(parents=True, exist_ok=True)
        for item in prepared_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, data_dir / item.name)
        os.chdir(repo_dir)
        sys.path.insert(0, str(repo_dir))
        sys.argv = [
            "main.py",
            "--dataset", {json.dumps(prepared.dataset_name)},
            "--use_gpu", "0",
            "--epoch", "1",
            "--eva_interval", "1",
            "--batch_size", "2",
            "--suffix", "smoke",
            "--log", "0",
            "--tensorboard", "0",
            "--save", "0",
            "--exp_mode", "ff",
            "--early_stop", "1",
            "--topk", "[1]",
        ]
        runpy.run_path("main.py", run_name="__main__")
        print("JSON_RESULT=" + json.dumps({{
            "metrics": {{"ENTRYPOINT_EXECUTED": 1.0}},
            "notes": ["Executed the upstream I3-MRec smoke path on the prepared presplit dataset."],
        }}, sort_keys=True))
        """
    )
    return _run_python_snippet(snippet, cwd=run_dir)


def _default_guided_mmrec_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    repo_dir = Path(str(prepared.metadata["repo_dir"]))
    snippet = textwrap.dedent(
        f"""
        import json
        from pathlib import Path
        import os
        import sys
        import types
        import numpy as np
        import torch
        import torch.nn as nn

        np.float = float
        np.int = int
        torch.Tensor.cuda = lambda self, *args, **kwargs: self
        nn.Module.cuda = lambda self, *args, **kwargs: self

        class _Identity:
            def __init__(self, *args, **kwargs):
                pass
            def __call__(self, value, *args, **kwargs):
                return value

        def _compose(steps):
            def _apply(value):
                for step in steps:
                    value = step(value)
                return value
            return _apply

        functional = types.SimpleNamespace(pad=lambda img,*a,**k: img, resize=lambda img,*a,**k: img)
        transforms_mod = types.SimpleNamespace(Compose=_compose, Resize=_Identity, Pad=_Identity, ToTensor=_Identity, functional=functional)
        sys.modules["torchvision"] = types.SimpleNamespace(transforms=transforms_mod)
        sys.modules["torchvision.transforms"] = transforms_mod
        sys.modules["torchvision.transforms.functional"] = functional
        sys.modules["geomloss"] = types.SimpleNamespace(SamplesLoss=lambda *a, **k: (lambda *aa, **kk: torch.tensor(0.0)))

        repo_dir = Path({json.dumps(str(repo_dir))})
        prepared_dir = Path({json.dumps(str(prepared.output_dir))})
        os.chdir(repo_dir / "src")
        sys.path.insert(0, str(repo_dir / "src"))

        from utils.configurator import Config
        from utils.dataset import RecDataset
        from utils.dataloader import TrainDataLoader
        from utils.utils import init_seed, get_model

        student_config_dict = {{
            "model": "BM3",
            "dataset": prepared_dir.name,
            "data_path": str(prepared_dir.parent) + "/",
            "inter_file_name": {json.dumps(str(prepared.metadata["inter_file_name"]))},
            "vision_feature_file": {json.dumps(str(prepared.metadata["image_feature_file"]))},
            "text_feature_file": {json.dumps(str(prepared.metadata["text_feature_file"]))},
            "field_separator": "\\t",
            "USER_ID_FIELD": "userID",
            "ITEM_ID_FIELD": "itemID",
            "TIME_FIELD": "timestamp",
            "inter_splitting_label": "x_label",
            "filter_out_cod_start_users": True,
            "gpu_id": 0,
            "use_gpu": False,
            "seed": [0],
            "epochs": 1,
            "eval_step": 1,
            "stopping_step": 1,
            "train_batch_size": 2,
            "eval_batch_size": 2,
            "metrics": ["Recall", "NDCG"],
            "topk": [2],
            "valid_metric": "Recall@2",
            "hyper_parameters": ["seed"],
            "save_recommended_topk": False,
            "n_layers": 1,
            "dropout": 0.3,
            "reg_weight": 0.1,
            "weight_decay": 0.0,
        }}
        teacher_config_dict = dict(student_config_dict)
        teacher_config_dict.update({{"model": "GUIDER", "n_ui_layers": 1, "n_mm_layers": 1, "knn_k": 1, "reg_weight": 1e-4, "weight_size": 64}})

        student_config = Config("BM3", prepared_dir.name, student_config_dict, False)
        teacher_config = Config("GUIDER", prepared_dir.name, teacher_config_dict, False)
        init_seed(0)
        dataset = RecDataset(student_config)
        str(dataset)
        train_dataset, valid_dataset, test_dataset = dataset.split()
        str(train_dataset); str(valid_dataset); str(test_dataset)
        student_train_data = TrainDataLoader(student_config, train_dataset, batch_size=student_config["train_batch_size"], shuffle=True)
        teacher_train_data = TrainDataLoader(teacher_config, train_dataset, batch_size=teacher_config["train_batch_size"], shuffle=True)
        student_model = get_model("BM3")(student_config, student_train_data).to(student_config["device"])
        teacher_model = get_model("GUIDER")(teacher_config, teacher_train_data).to(teacher_config["device"])
        print("JSON_RESULT=" + json.dumps({{
            "metrics": {{
                "ENTRYPOINT_EXECUTED": 1.0,
                "STUDENT_PARAM_COUNT": float(sum(p.numel() for p in student_model.parameters())),
                "TEACHER_PARAM_COUNT": float(sum(p.numel() for p in teacher_model.parameters())),
            }},
            "notes": ["Executed the upstream Guider smoke path on the prepared presplit dataset."],
        }}, sort_keys=True))
        """
    )
    return _run_python_snippet(snippet, cwd=run_dir)


def _default_diffmm_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    repo_dir = Path(str(prepared.metadata["repo_dir"]))
    snippet = textwrap.dedent(
        f"""
        import json
        from pathlib import Path
        import os
        import pickle
        import sys
        import types
        import numpy as np
        import torch
        import torch.nn as nn

        torch.Tensor.cuda = lambda self, *args, **kwargs: self
        nn.Module.cuda = lambda self, *args, **kwargs: self
        sys.modules["setproctitle"] = types.SimpleNamespace(setproctitle=lambda *a, **k: None)

        repo_dir = Path({json.dumps(str(repo_dir))})
        prepared_dir = Path({json.dumps(str(prepared.output_dir))})
        dataset_dir = repo_dir / "Datasets" / "baby"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        for name in ["trnMat.pkl", "tstMat.pkl", "image_feat.npy", "text_feat.npy"]:
            src = prepared_dir / name
            dst = dataset_dir / name
            if src.suffix == ".pkl":
                with src.open("rb") as handle:
                    payload = pickle.load(handle)
                with dst.open("wb") as handle:
                    pickle.dump(payload, handle)
            else:
                import shutil
                shutil.copy2(src, dst)

        os.chdir(repo_dir)
        sys.path.insert(0, str(repo_dir))
        from Params import args
        from DataHandler import DataHandler
        args.data = "baby"
        args.batch = 2
        args.tstBat = 2
        args.epoch = 1
        args.tstEpoch = 1
        args.gpu = "0"
        handler = DataHandler()
        handler.LoadData()
        print("JSON_RESULT=" + json.dumps({{
            "metrics": {{
                "ENTRYPOINT_EXECUTED": 1.0,
                "USER_COUNT": float(args.user),
                "ITEM_COUNT": float(args.item),
            }},
            "notes": ["Loaded the upstream DiffMM data handler on the prepared presplit dataset."],
        }}, sort_keys=True))
        """
    )
    return _run_python_snippet(snippet, cwd=run_dir)


def _default_graph_imputation_executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
    repo_dir = Path(str(prepared.metadata["repo_dir"]))
    snippet = textwrap.dedent(
        f"""
        import json
        from pathlib import Path
        import os
        import runpy
        import shutil
        import sys
        import types
        import numpy as np

        class _Storage:
            def __init__(self, row, col, value):
                self._row = np.array(row)
                self._col = np.array(col)
                self._value = np.array(value)

        class _RowView:
            def __init__(self, cols):
                self.storage = types.SimpleNamespace(_col=np.array(cols, dtype=np.int64))

        class SparseTensor:
            def __init__(self, row, col, value, sparse_sizes):
                self.storage = _Storage(row, col, value)
                self.sparse_sizes = sparse_sizes
            def __getitem__(self, idx):
                mask = self.storage._row == idx
                return _RowView(self.storage._col[mask])

        def fill_diag(adj, fill_value=0.):
            return adj

        def sum_fn(adj, dim=-1):
            return np.zeros(adj.sparse_sizes[0], dtype=np.float32)

        def mul(adj, values):
            return adj

        def matmul(adj, matrix):
            return matrix

        sys.modules["torch_sparse"] = types.SimpleNamespace(
            SparseTensor=SparseTensor,
            fill_diag=fill_diag,
            sum=sum_fn,
            mul=mul,
            matmul=matmul,
        )

        repo_dir = Path({json.dumps(str(repo_dir))})
        prepared_dir = Path({json.dumps(str(prepared.output_dir))})
        upstream_data = repo_dir / "data" / {json.dumps(prepared.dataset_name)}
        upstream_data.mkdir(parents=True, exist_ok=True)
        for item in prepared_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, upstream_data / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, upstream_data / item.name)

        missing_index = 1 if int({json.dumps(int(prepared.metadata["item_count"]))}) > 1 else 0
        for name in ["missing_visual.tsv", "missing_textual.tsv", "missing_visual_indexed.tsv", "missing_textual_indexed.tsv"]:
            (upstream_data / name).write_text(f"{{missing_index}}\\n", encoding="utf-8")
        for folder in ["visual_embeddings_indexed", "textual_embeddings_indexed"]:
            target = upstream_data / folder / f"{{missing_index}}.npy"
            if target.exists():
                target.unlink()

        os.chdir(repo_dir)
        sys.path.insert(0, str(repo_dir))
        sys.argv = ["impute.py", "--data", {json.dumps(prepared.dataset_name)}, "--method", "neigh_mean", "--top_k", "1"]
        runpy.run_path("impute.py", run_name="__main__")
        output_path = upstream_data / "visual_embeddings_neigh_mean_1_indexed" / f"{{missing_index}}.npy"
        print("JSON_RESULT=" + json.dumps({{
            "metrics": {{"ENTRYPOINT_EXECUTED": 1.0, "IMPUTED_VISUAL_EXISTS": float(output_path.exists())}},
            "notes": ["Executed the upstream graph-imputation smoke path on the prepared indexed dataset."],
        }}, sort_keys=True))
        """
    )
    return _run_python_snippet(snippet, cwd=run_dir)


def _default_unimplemented_executor(mode: str) -> BaselineExecutor:
    def _executor(record: dict, prepared: PreparedBaselineDataset, run_dir: Path) -> dict:
        raise NotImplementedError(
            f"Default executor for integration mode '{mode}' is not wired yet; use an injected executor or a task-specific runtime hook."
        )

    return _executor


def _prepare_dataset(record: dict, request: BaselineRunRequest, run_dir: Path) -> PreparedBaselineDataset:
    integration_mode = record["integration_mode"]
    prepared_root = run_dir / "prepared"

    if integration_mode == "recbole":
        return _prepare_recbole_dataset(request.dataset_name, request.source_dir, prepared_root, request.baseline_name)

    if integration_mode == "vbpr_python":
        prepared = prepare_vbpr_dataset(request.dataset_name, request.source_dir, prepared_root)
        if record.get("source_path"):
            extracted = extract_baseline_archive(Path(record["source_path"]), run_dir / "repo")
            prepared.metadata["repo_dir"] = str(extracted.extracted_dir)
        return prepared

    if integration_mode == "guided_mmrec":
        prepared = prepare_mmrec_dataset(request.dataset_name, request.source_dir, prepared_root / "dataset")
        if record.get("source_path"):
            extracted = extract_baseline_archive(Path(record["source_path"]), run_dir / "repo")
            prepared.metadata["repo_dir"] = str(extracted.extracted_dir)
            prepared.metadata["repo_entry_dir"] = str(extracted.extracted_dir / "src")
        return prepared

    if integration_mode == "mmrec":
        prepared = prepare_mmrec_dataset(request.dataset_name, request.source_dir, prepared_root / "dataset")
        if record.get("source_path"):
            extracted = extract_baseline_archive(Path(record["source_path"]), run_dir / "repo")
            prepared.metadata["repo_dir"] = str(extracted.extracted_dir)
            repo_entry_dir = extracted.extracted_dir / "src" if (extracted.extracted_dir / "src").exists() else extracted.extracted_dir
            prepared.metadata["repo_entry_dir"] = str(repo_entry_dir)
        return prepared

    if integration_mode == "diffmm":
        prepared = prepare_diffmm_dataset(request.dataset_name, request.source_dir, prepared_root / "dataset")
        if record.get("source_path"):
            extracted = extract_baseline_archive(Path(record["source_path"]), run_dir / "repo")
            prepared.metadata["repo_dir"] = str(extracted.extracted_dir)
        return prepared

    if integration_mode == "i3mrec":
        prepared = prepare_i3mrec_dataset(request.dataset_name, request.source_dir, prepared_root / "dataset")
        if record.get("source_path"):
            extracted = extract_baseline_archive(Path(record["source_path"]), run_dir / "repo")
            prepared.metadata["repo_dir"] = str(extracted.extracted_dir)
        return prepared

    if integration_mode == "graph_imputation":
        prepared = prepare_graph_imputation_dataset(request.dataset_name, request.source_dir, prepared_root / "dataset")
        if record.get("source_path"):
            extracted = extract_baseline_archive(Path(record["source_path"]), run_dir / "repo")
            prepared.metadata["repo_dir"] = str(extracted.extracted_dir)
        return prepared

    raise ValueError(f"Unsupported integration mode: {integration_mode}")


def run_baseline(
    request: BaselineRunRequest,
    executors: dict[str, BaselineExecutor] | None = None,
) -> BaselineRunResult:
    record = _get_baseline_record(request.baseline_name, Path(request.baselines_dir))
    status = record["status"]
    if status == "missing":
        raise ValueError(f"Baseline asset is not available locally: {request.baseline_name}")
    if status == "asset_mismatch":
        raise ValueError(f"Baseline asset_mismatch: {request.baseline_name}. {record['notes']}")
    if status == "asset_incomplete":
        raise ValueError(f"Baseline asset_incomplete: {request.baseline_name}. {record['notes']}")
    if status == "runtime_mismatch":
        raise ValueError(f"Baseline runtime_mismatch: {request.baseline_name}. {record['notes']}")

    run_dir = _prepare_run_directory(request.results_root, request.baseline_name, request.run_id)
    prepared = _prepare_dataset(record, request, run_dir)

    executors = executors or {}
    integration_mode = record["integration_mode"]
    default_executors: dict[str, BaselineExecutor] = {
        "recbole": _default_recbole_executor,
        "vbpr_python": _default_vbpr_executor,
        "guided_mmrec": _default_guided_mmrec_executor,
        "mmrec": _default_mmrec_executor,
        "diffmm": _default_diffmm_executor,
        "i3mrec": _default_i3mrec_executor,
        "graph_imputation": _default_graph_imputation_executor,
    }
    executor = executors.get(integration_mode, default_executors[integration_mode])
    metrics, notes = _normalize_executor_output(executor(record, prepared, run_dir))
    result = BaselineRunResult(
        baseline_name=request.baseline_name,
        dataset_name=request.dataset_name,
        integration_mode=integration_mode,
        run_id=request.run_id,
        run_dir=run_dir,
        metrics=metrics,
        notes=notes,
    )
    _write_run_outputs(result)
    return result
