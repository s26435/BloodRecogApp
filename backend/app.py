from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import dotenv
from src.analysis_service import process_analysis, list_analyses, get_analysis, UPLOADS_DIR
dotenv.load_dotenv()

#Ścieżki 
BASE_DIR = Path(__file__).resolve().parent        
ROOT_DIR = BASE_DIR.parent                        
FRONTEND_DIR = ROOT_DIR / "frontend"              
(FRONTEND_DIR / "uploads").mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

#FRONTEND
@app.get("/", response_class=FileResponse)
async def serve_home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/upload", response_class=FileResponse)
async def serve_upload():
    return FileResponse(FRONTEND_DIR / "upload.html")


@app.get("/history", response_class=FileResponse)
async def serve_history():
    return FileResponse(FRONTEND_DIR / "history.html")


@app.get("/model", response_class=FileResponse)
async def serve_model():
    return FileResponse(FRONTEND_DIR / "index.html")

#helth - checkup
@app.get("/helth/")
def health():
    return {"status": "ok"}


#API: ANALIZY
# CREATE – tworzenie nowej analizy po kliknięciu Uruchom analizę
#/api/analyses i /api/analyses/ żeby pasowało do JS
@app.post("/api/analyses", response_class=JSONResponse)
@app.post("/api/analyses/", response_class=JSONResponse)
async def create_analysis(
    analysis_name: str = Form(...),
    analysis_notes: str = Form(""),
    analysis_image: UploadFile = File(...),
):
    if analysis_image.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=400,
            detail=f"Nieobsługiwany typ pliku: {analysis_image.content_type}. Dozwolone: JPG/PNG",
        )

    contents = await analysis_image.read()

    try:
        record = process_analysis(
            image_bytes=contents,
            content_type=analysis_image.content_type,
            name=analysis_name,
            notes=analysis_notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "analysis": record}


# LIST – dla historii (history.js → fetch("/api/analyses/"))
@app.get("/api/analyses", response_class=JSONResponse)
@app.get("/api/analyses/", response_class=JSONResponse)
def api_list_analyses():
    return list_analyses()


# DETAIL – gdybyś kiedyś chciał wyświetlać szczegóły po ID z backendu
@app.get("/api/analyses/{analysis_id}", response_class=JSONResponse)
@app.get("/api/analyses/{analysis_id}/", response_class=JSONResponse)
def api_get_analysis(analysis_id: str):
    record = get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono analizy")
    return record
