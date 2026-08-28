from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_pipeline


app = FastAPI(
    title="Clarix API",
    description="Backend API for Clarix satellite image analysis",
    version="1.0.0",
)

# Allow the Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "backend_data" / "uploads"
RESULT_DIR = BASE_DIR / "backend_data" / "results"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "Clarix API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    allowed_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
    }

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )

    job_id = uuid.uuid4().hex

    input_path = UPLOAD_DIR / f"{job_id}{extension}"
    output_dir = RESULT_DIR / job_id

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save uploaded image
    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run processing pipeline
    result = run_pipeline(
        input_path=input_path,
        output_dir=output_dir,
    )

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "result": result,
    }