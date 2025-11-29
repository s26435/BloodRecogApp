import io
from pathlib import Path

from PIL import Image

from fastapi import FastAPI, UploadFile, File, HTTPException
from src.utils import build_predictor, run_inference_on_image
from src.train import train_new_model
from src.download_ds import download_ds

import dotenv
dotenv.load_dotenv()

OUT_DIR: Path = Path("out")
DS_DIR: Path = Path("Blood-1")

if not OUT_DIR.exists() or not Path(OUT_DIR / "model_final.pth").exists():
    if not DS_DIR.exists():
        download_ds()
    train_new_model(str(OUT_DIR))

predictor, infer_cfg = build_predictor(str(OUT_DIR))

app = FastAPI()

@app.get("/helth/")
def health():
    return {"status": "ok"}


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=400,
            detail=f"Nieobsługiwany typ pliku: {file.content_type}. JPG/PNG",
        )

    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Nie udało się odczytać obrazu",
        )
    
    return run_inference_on_image(predictor, infer_cfg, image)
