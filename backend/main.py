from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.pipeline import run_pipeline


# --------------------------------------------------
# Project directories
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_DATA_DIR = BASE_DIR / "backend_data"

UPLOAD_DIR = BACKEND_DATA_DIR / "uploads"
RESULT_DIR = BACKEND_DATA_DIR / "results"
SR_DIR = BACKEND_DATA_DIR / "sr"
RAW_DIR = BACKEND_DATA_DIR / "raw"
HR_DIR = BACKEND_DATA_DIR / "hr"
LR_DIR = BACKEND_DATA_DIR / "lr"

for directory in [
    BACKEND_DATA_DIR,
    UPLOAD_DIR,
    RESULT_DIR,
    SR_DIR,
    RAW_DIR,
    HR_DIR,
    LR_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Clarix API",
    description="Backend API for Clarix satellite image analysis",
    version="1.0.0",
)


# --------------------------------------------------
# Static pipeline files
# --------------------------------------------------

app.mount(
    "/pipeline-files",
    StaticFiles(directory=str(BACKEND_DATA_DIR)),
    name="pipeline-files",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

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


# --------------------------------------------------
# Basic endpoints
# --------------------------------------------------

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


# --------------------------------------------------
# SR result endpoint
# --------------------------------------------------

@app.get("/results/{job_id}/sr")
def get_sr_result(job_id: str):

    sr_files = list(
        SR_DIR.glob(
            f"{job_id}_*_sr_1024.png"
        )
    )

    if not sr_files:
        raise HTTPException(
            status_code=404,
            detail="SR result not found.",
        )

    return FileResponse(
        path=sr_files[0],
        media_type="image/png",
    )


# --------------------------------------------------
# Main analysis endpoint
# --------------------------------------------------

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # Validate filename
    # --------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    # --------------------------------------------------
    # Validate extension
    # --------------------------------------------------

    allowed_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
    }

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format.",
        )

    # --------------------------------------------------
    # Generate job ID
    # --------------------------------------------------

    job_id = uuid.uuid4().hex

    # Uploaded file stored using job ID
    input_path = UPLOAD_DIR / f"{job_id}{extension}"

    # Original filename without extension
    filename_stem = Path(file.filename).stem

    # --------------------------------------------------
    # Save uploaded image
    # --------------------------------------------------

    try:
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded image: {exc}",
        )

    # --------------------------------------------------
    # Run P2 -> P1 pipeline
    # --------------------------------------------------

    try:
        result = run_pipeline(
            input_path=str(input_path),
            output_name=f"{job_id}_{filename_stem}",
        )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {exc}",
        )

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "result": result,
    }

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "result": result,
    }

    raw_path = Path(result["raw"])
    sr_path = Path(result["sr"])

    # URL paths exposed by FastAPI StaticFiles
    raw_url = (
        f"/pipeline-files/"
        f"{raw_path.relative_to(BACKEND_DATA_DIR).as_posix()}"
    )

    sr_url = (
        f"/pipeline-files/"
        f"{sr_path.relative_to(BACKEND_DATA_DIR).as_posix()}"
    )

    frontend_result = {
        "jobId": job_id,

        "source": {
            "filename": file.filename,
            "width": 0,
            "height": 0,
            "size": input_path.stat().st_size,
        },

        "images": {
            "input": raw_url,

            # P3 not connected yet
            "bicubic": raw_url,

            # P1 ESRGAN output
            "clarix": sr_url,

            # P4 not connected yet
            "landCover": raw_url,
        },

        "metrics": {
            "psnr": None,
            "ssim": None,
            "scaleFactor": 4,
        },

        "landCover": [
            {
                "id": "vegetation",
                "label": "Vegetation",
                "color": "var(--vegetation)",
                "share": None,
            },
            {
                "id": "water",
                "label": "Water",
                "color": "var(--water)",
                "share": None,
            },
            {
                "id": "builtup",
                "label": "Built-up",
                "color": "var(--builtup)",
                "share": None,
            },
            {
                "id": "road",
                "label": "Road",
                "color": "var(--road)",
                "share": None,
            },
            {
                "id": "other",
                "label": "Other",
                "color": "var(--muted-foreground)",
                "share": None,
            },
        ],
    }

    # --------------------------------------------------
    # Final response
    # --------------------------------------------------

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "result": frontend_result,
    }