from __future__ import annotations
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image
from src.utils import build_predictor, run_inference_on_image
from src.train import train_new_model
from src.download_ds import download_ds

OUT_DIR: Path = Path("out")
DS_DIR: Path = Path("Blood-1")
BASE_DIR = Path(__file__).resolve().parent 
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
UPLOADS_DIR: Path = FRONTEND_DIR / "uploads"
DATA_DIR: Path = ROOT_DIR / "Data"
ANALYSES_DB_PATH: Path = DATA_DIR / "analyses.json"


def _ensure_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_model() -> Tuple[Any, Any]:
    _ensure_dirs()

    if not OUT_DIR.exists() or not (OUT_DIR / "model_final.pth").exists():
        if not DS_DIR.exists():
            download_ds()
        train_new_model(str(OUT_DIR))

    predictor, infer_cfg = build_predictor(str(OUT_DIR))
    return predictor, infer_cfg

_predictor, _infer_cfg = _ensure_model()


def load_analyses() -> List[Dict[str, Any]]:
    if not ANALYSES_DB_PATH.exists():
        return []
    try:
        with open(ANALYSES_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_analyses(analyses: List[Dict[str, Any]]) -> None:
    ANALYSES_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ANALYSES_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(analyses, f, ensure_ascii=False, indent=2)


def generate_analysis_id() -> str:
    return datetime.now().strftime("A%Y%m%d%H%M%S%f")


def process_analysis(
    image_bytes: bytes,
    content_type: str,
    name: str,
    notes: str = "",
) -> Dict[str, Any]:
    _ensure_dirs()

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("Nie udało się odczytać obrazu") from exc

    vis_image = run_inference_on_image(_predictor, _infer_cfg, np.array(image))
    result_np = vis_image.get_image()
    result_image = Image.fromarray(result_np)

    analysis_id = generate_analysis_id()
    orig_filename = f"{analysis_id}_orig.png"
    result_filename = f"{analysis_id}_result.png"

    orig_path = UPLOADS_DIR / orig_filename
    result_path = UPLOADS_DIR / result_filename

    image.save(orig_path)
    result_image.save(result_path)

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    record: Dict[str, Any] = {
        "id": analysis_id,
        "name": name or analysis_id,
        "created_at": created_at,
        "original_image_url": f"/static/uploads/{orig_filename}",
        "processed_image_url": f"/static/uploads/{result_filename}",
        "notes": notes or "",
    }

    analyses = load_analyses()
    analyses.append(record)
    save_analyses(analyses)

    return record


def list_analyses() -> List[Dict[str, Any]]:
    return load_analyses()


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    for a in load_analyses():
        if a.get("id") == analysis_id:
            return a
    return None





