from pathlib import Path

import shutil
from PIL import Image

from backend import backend


# --------------------------------------------------
# Project directories
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_DATA_DIR = BASE_DIR / "backend_data"

RAW_DIR = BACKEND_DATA_DIR / "raw"
HR_DIR = BACKEND_DATA_DIR / "hr"
LR_DIR = BACKEND_DATA_DIR / "lr"
SR_DIR = BACKEND_DATA_DIR / "sr"

for directory in [
    RAW_DIR,
    HR_DIR,
    LR_DIR,
    SR_DIR
]:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# --------------------------------------------------
# P2 PREPROCESSING
# --------------------------------------------------

def preprocess_image(
    image_path: Path,
    output_name: str
):
    """
    P2 preprocessing.

    Converts the image to RGB, center-crops it,
    creates a 512x512 HR reference image,
    and creates a 256x256 LR image.
    """

    img = Image.open(image_path)

    print(f"Original size: {img.size}")
    print(f"Original mode: {img.mode}")

    # Convert to RGB
    img = img.convert("RGB")

    # Center crop to square
    width, height = img.size

    side = min(width, height)

    left = (width - side) // 2
    top = (height - side) // 2

    right = left + side
    bottom = top + side

    img_square = img.crop(
        (left, top, right, bottom)
    )

    # Create HR reference
    img_hr = img_square.resize(
        (512, 512),
        Image.Resampling.LANCZOS
    )

    # Create LR image
    img_lr = img_hr.resize(
        (256, 256),
        Image.Resampling.BICUBIC
    )

    # Output paths
    hr_path = HR_DIR / f"{output_name}_hr_512.png"
    lr_path = LR_DIR / f"{output_name}_lr_256.png"

    img_hr.save(hr_path)
    img_lr.save(lr_path)

    print(f"HR saved to: {hr_path}")
    print(f"LR saved to: {lr_path}")

    return hr_path, lr_path


# --------------------------------------------------
# COMPLETE P2 → P1 → P3 PIPELINE
# --------------------------------------------------

def run_pipeline(
    input_path: str,
    output_name: str
):
    """
    Run:

        Uploaded Image
              ↓
        P2 Preprocessing
              ↓
          LR 256x256
              ↓
       ┌──────┴──────┐
       ↓             ↓
      P1             P3
   Real-ESRGAN      Bicubic
       ↓             ↓
    SR 1024       Bicubic 1024
    """

    input_path = Path(input_path)

    # --------------------------------------------------
    # STEP 1: Store raw input
    # --------------------------------------------------

    raw_path = RAW_DIR / input_path.name

    shutil.copy2(
        input_path,
        raw_path
    )

    # --------------------------------------------------
    # STEP 2: P2 preprocessing
    # --------------------------------------------------

    hr_path, lr_path = preprocess_image(
        raw_path,
        output_name
    )

    # --------------------------------------------------
    # STEP 3: P1 Super Resolution
    # --------------------------------------------------

    sr_path = SR_DIR / f"{output_name}_sr_1024.png"

    print("Starting P1 super-resolution...")

    model, device = backend.get_sr_model()

    backend.run_super_resolution(
        input_path=str(lr_path),
        output_path=str(sr_path),
        model=model,
        device=device
    )

    print(f"SR saved to: {sr_path}")

    # --------------------------------------------------
    # STEP 4: P3 Bicubic Baseline
    # --------------------------------------------------

    bicubic_path = SR_DIR / f"{output_name}_bicubic_1024.png"

    print("Starting P3 bicubic upscaling...")

    backend.run_bicubic(
        input_path=str(lr_path),
        output_path=str(bicubic_path)
    )

    print(f"Bicubic saved to: {bicubic_path}")

    # --------------------------------------------------
    # STEP 5: Return pipeline results
    # --------------------------------------------------

    return {
        "raw": str(raw_path),
        "hr": str(hr_path),
        "lr": str(lr_path),
        "sr": str(sr_path),
        "bicubic": str(bicubic_path)
    }