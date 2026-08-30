from pathlib import Path
import shutil
import sys
import time

import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity

from backend import backend


# ==================================================
# PROJECT DIRECTORIES
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_DATA_DIR = BASE_DIR / "backend_data"

RAW_DIR = BACKEND_DATA_DIR / "raw"
HR_DIR = BACKEND_DATA_DIR / "hr"
LR_DIR = BACKEND_DATA_DIR / "lr"
SR_DIR = BACKEND_DATA_DIR / "sr"
P4_DIR = BACKEND_DATA_DIR / "p4"


for directory in [
    RAW_DIR,
    HR_DIR,
    LR_DIR,
    SR_DIR,
    P4_DIR,
]:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


# ==================================================
# PSNR / SSIM
# ==================================================

def calculate_psnr(reference, reconstructed):

    if reference.shape != reconstructed.shape:
        raise ValueError(
            "Reference and reconstructed images "
            "must have the same dimensions."
        )

    return cv2.PSNR(
        reference,
        reconstructed,
    )


def calculate_ssim(reference, reconstructed):

    if reference.shape != reconstructed.shape:
        raise ValueError(
            "Reference and reconstructed images "
            "must have the same dimensions."
        )

    reference_gray = cv2.cvtColor(
        reference,
        cv2.COLOR_BGR2GRAY,
    )

    reconstructed_gray = cv2.cvtColor(
        reconstructed,
        cv2.COLOR_BGR2GRAY,
    )

    return structural_similarity(
        reference_gray,
        reconstructed_gray,
        data_range=255,
    )


def calculate_image_metrics(
    reference_path: str,
    reconstructed_path: str,
):

    reference = cv2.imread(
        str(reference_path)
    )

    reconstructed = cv2.imread(
        str(reconstructed_path)
    )

    if reference is None:
        raise FileNotFoundError(
            f"Could not read reference image: "
            f"{reference_path}"
        )

    if reconstructed is None:
        raise FileNotFoundError(
            f"Could not read reconstructed image: "
            f"{reconstructed_path}"
        )

    print(
        f"Reference shape: {reference.shape}"
    )

    print(
        f"Reconstructed shape: {reconstructed.shape}"
    )

    if reference.shape != reconstructed.shape:
        raise ValueError(
            "Reference and reconstructed images "
            f"must have the same dimensions. "
            f"Reference: {reference.shape}, "
            f"Reconstructed: {reconstructed.shape}"
        )

    psnr = calculate_psnr(
        reference,
        reconstructed,
    )

    ssim = calculate_ssim(
        reference,
        reconstructed,
    )

    return {
        "psnr": float(psnr),
        "ssim": float(ssim),
    }


# ==================================================
# P2 PREPROCESSING
# ==================================================

def preprocess_image(
    image_path: Path,
    output_name: str,
):

    """
    Pipeline:

        Original
            ↓
        Center crop
            ↓
        HR = 512x512
            ↓
        LR = 128x128
    """

    img = Image.open(
        image_path
    )

    print(
        f"Original size: {img.size}"
    )

    print(
        f"Original mode: {img.mode}"
    )

    img = img.convert("RGB")

    # --------------------------------------------------
    # Center crop to square
    # --------------------------------------------------

    width, height = img.size

    side = min(
        width,
        height,
    )

    left = (
        width - side
    ) // 2

    top = (
        height - side
    ) // 2

    right = left + side
    bottom = top + side

    img_square = img.crop(
        (
            left,
            top,
            right,
            bottom,
        )
    )

    # --------------------------------------------------
    # HR = 512x512
    # --------------------------------------------------

    img_hr = img_square.resize(
        (512, 512),
        Image.Resampling.LANCZOS,
    )

    # --------------------------------------------------
    # LR = 128x128
    # --------------------------------------------------

    img_lr = img_hr.resize(
        (128, 128),
        Image.Resampling.BICUBIC,
    )

    # --------------------------------------------------
    # Paths
    # --------------------------------------------------

    hr_path = (
        HR_DIR
        / f"{output_name}_hr_512.png"
    )

    lr_path = (
        LR_DIR
        / f"{output_name}_lr_128.png"
    )

    img_hr.save(
        hr_path
    )

    img_lr.save(
        lr_path
    )

    print(
        f"HR saved to: {hr_path}"
    )

    print(
        f"LR saved to: {lr_path}"
    )

    return hr_path, lr_path


# ==================================================
# FORCE IMAGE TO 512x512
# ==================================================

def ensure_512x512(
    image_path: str,
):

    image_path = Path(
        image_path
    )

    img = Image.open(
        image_path
    ).convert("RGB")

    print(
        f"Image size before check: "
        f"{img.size}"
    )

    if img.size != (512, 512):

        print(
            "Resizing image to 512x512..."
        )

        img = img.resize(
            (512, 512),
            Image.Resampling.BICUBIC,
        )

        img.save(
            image_path
        )

    print(
        f"Final image size: "
        f"{Image.open(image_path).size}"
    )

    return image_path


# ==================================================
# P4 SEGMENTATION
# ==================================================

def run_p4_segmentation(
    input_path: str,
    output_path: str,
):

    print(
        "Starting P4 segmentation..."
    )

    print(
        f"P4 input: {input_path}"
    )

    input_path = Path(
        input_path
    )

    output_path = Path(
        output_path
    )

    if not input_path.exists():

        raise FileNotFoundError(
            f"P4 input image not found: "
            f"{input_path}"
        )

    # --------------------------------------------------
    # P4 directory
    # --------------------------------------------------

    p4_dir = (
        BASE_DIR
        / "Mapping-Segmentation"
    )

    if not p4_dir.exists():

        raise FileNotFoundError(
            f"P4 directory not found: "
            f"{p4_dir}"
        )

    p4_dir_str = str(
        p4_dir
    )

    if p4_dir_str not in sys.path:

        sys.path.insert(
            0,
            p4_dir_str,
        )

    # --------------------------------------------------
    # Import inference
    # --------------------------------------------------

    try:

        from inference_512 import (
            run_segmentation
        )

    except Exception as exc:

        raise RuntimeError(
            "Could not import P4 "
            "inference_512.py. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------
    # Run segmentation
    # --------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = run_segmentation(
        str(input_path),
        str(output_path.parent),
    )

    if result is None:

        raise RuntimeError(
            "P4 segmentation failed."
        )

    result_path = Path(
        result
    )

    # --------------------------------------------------
    # Rename output
    # --------------------------------------------------

    if result_path != output_path:

        if output_path.exists():

            output_path.unlink()

        shutil.move(
            str(result_path),
            str(output_path),
        )

    print(
        f"P4 mask saved to: "
        f"{output_path}"
    )

    return str(
        output_path
    )


# ==================================================
# LAND COVER
# ==================================================

def calculate_land_cover(
    mask_path: str,
):

    mask = np.load(
        mask_path
    )

    if mask.ndim != 2:

        raise ValueError(
            f"Expected 2D segmentation mask, "
            f"got shape {mask.shape}"
        )

    total_pixels = mask.size

    if total_pixels == 0:

        raise ValueError(
            "Segmentation mask contains no pixels."
        )

    # --------------------------------------------------
    # P4 -> Frontend
    # --------------------------------------------------

    CLASS_TO_FRONTEND = {

        1: "vegetation",

        2: "water",

        5: "builtup",

        6: "road",
    }

    # --------------------------------------------------
    # Frontend classes
    # --------------------------------------------------

    land_cover = [

        {
            "id": "vegetation",
            "label": "Vegetation",
            "color": "var(--vegetation)",
            "share": 0.0,
        },

        {
            "id": "water",
            "label": "Water",
            "color": "var(--water)",
            "share": 0.0,
        },

        {
            "id": "builtup",
            "label": "Built-up",
            "color": "var(--builtup)",
            "share": 0.0,
        },

        {
            "id": "road",
            "label": "Road",
            "color": "var(--road)",
            "share": 0.0,
        },

        {
            "id": "other",
            "label": "Other",
            "color": "var(--muted-foreground)",
            "share": 0.0,
        },
    ]

    # --------------------------------------------------
    # Count classes
    # --------------------------------------------------

    unique_classes, class_counts = np.unique(
        mask,
        return_counts=True,
    )

    counts = {

        int(class_id): int(count)

        for class_id, count in zip(
            unique_classes,
            class_counts,
        )
    }

    print(
        "P4 mask class counts:"
    )

    for class_id, count in sorted(
        counts.items()
    ):

        percentage = (
            count
            / total_pixels
        ) * 100

        print(
            f"  Class {class_id}: "
            f"{count} pixels "
            f"({percentage:.2f}%)"
        )

    # --------------------------------------------------
    # Calculate shares
    # --------------------------------------------------

    for item in land_cover:

        frontend_id = item["id"]

        matching_class_ids = [

            class_id

            for class_id, mapped_id
            in CLASS_TO_FRONTEND.items()

            if mapped_id == frontend_id
        ]

        pixel_count = sum(

            counts.get(
                class_id,
                0,
            )

            for class_id
            in matching_class_ids
        )

        item["share"] = (

            pixel_count
            / total_pixels

        )

    # --------------------------------------------------
    # Other
    # --------------------------------------------------

    mapped_class_ids = set(
        CLASS_TO_FRONTEND.keys()
    )

    other_pixel_count = sum(

        count

        for class_id, count
        in counts.items()

        if class_id
        not in mapped_class_ids
    )

    other_item = next(

        item

        for item in land_cover

        if item["id"] == "other"
    )

    other_item["share"] = (

        other_pixel_count
        / total_pixels
    )

    print("")
    print("Land-cover:")

    for item in land_cover:

        print(

            f"  {item['label']}: "
            f"{item['share'] * 100:.2f}%"
        )

    print("")

    return land_cover


# ==================================================
# SEGMENTATION VISUALIZATION
# ==================================================

def create_segmentation_visualization(
    mask_path: str,
    output_path: str,
):

    print(
        "Creating P4 segmentation visualization..."
    )

    mask = np.load(
        mask_path
    )

    if mask.ndim != 2:

        raise ValueError(
            f"Expected a 2D segmentation mask, "
            f"got shape {mask.shape}"
        )

    height, width = mask.shape

    print(
        f"Segmentation visualization size: "
        f"{width}x{height}"
    )

    CLASS_COLORS = {

        1: (76, 175, 80),

        2: (33, 150, 243),

        5: (190, 70, 220),

        6: (90, 220, 220),
    }

    OTHER_COLOR = (
        120,
        130,
        140,
    )

    visualization = np.zeros(
        (height, width, 3),
        dtype=np.uint8,
    )

    visualization[:, :] = OTHER_COLOR

    for class_id, color in CLASS_COLORS.items():

        visualization[
            mask == class_id
        ] = color

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    Image.fromarray(
        visualization,
        mode="RGB",
    ).save(
        output_path
    )

    print(
        f"P4 visualization saved to: "
        f"{output_path}"
    )

    return str(
        output_path
    )


# ==================================================
# COMPLETE PIPELINE
# ==================================================

def run_pipeline(
    input_path: str,
    output_name: str,
):

    # ==================================================
    # TOTAL PIPELINE TIMER
    # ==================================================

    total_start = time.perf_counter()

    print("")
    print("=" * 60)
    print("STARTING CLARIX PIPELINE")
    print("=" * 60)

    input_path = Path(
        input_path
    )

    # ==================================================
    # STEP 1 — RAW
    # ==================================================

    step_start = time.perf_counter()

    raw_path = (
        RAW_DIR
        / input_path.name
    )

    shutil.copy2(
        input_path,
        raw_path,
    )

    print(
        f"Raw image saved to: "
        f"{raw_path}"
    )

    print(
        f"[TIME] RAW COPY: "
        f"{time.perf_counter() - step_start:.2f} seconds"
    )

    # ==================================================
    # STEP 2 — P2
    # ==================================================

    print("")
    print("STEP 2: P2 PREPROCESSING")

    step_start = time.perf_counter()

    hr_path, lr_path = preprocess_image(
        raw_path,
        output_name,
    )

    print(
        f"[TIME] P2 PREPROCESSING: "
        f"{time.perf_counter() - step_start:.2f} seconds"
    )

    # ==================================================
    # STEP 3 — P1 ESRGAN
    # ==================================================

    print("")
    print("STEP 3: P1 ESRGAN")

    # --------------------------------------------------
    # Model loading timer
    # --------------------------------------------------

    model_start = time.perf_counter()

    sr_model, device = (
        backend.get_sr_model()
    )

    model_time = (
        time.perf_counter()
        - model_start
    )

    print(
        f"[TIME] P1 MODEL LOAD/REUSE: "
        f"{model_time:.2f} seconds"
    )

    # --------------------------------------------------
    # ESRGAN inference timer
    # --------------------------------------------------

    sr_start = time.perf_counter()

    sr_path = (
        SR_DIR
        / f"{output_name}_sr_512.png"
    )

    backend.run_super_resolution(
        input_path=str(lr_path),
        output_path=str(sr_path),
        model=sr_model,
        device=device,
    )

    sr_inference_time = (
        time.perf_counter()
        - sr_start
    )

    print(
        f"[TIME] P1 ESRGAN INFERENCE: "
        f"{sr_inference_time:.2f} seconds"
    )

    # --------------------------------------------------
    # Ensure ESRGAN = 512x512
    # --------------------------------------------------

    ensure_start = time.perf_counter()

    ensure_512x512(
        sr_path
    )

    print(
        f"[TIME] P1 SIZE CHECK: "
        f"{time.perf_counter() - ensure_start:.2f} seconds"
    )

    print(
        f"SR saved to: "
        f"{sr_path}"
    )

    # ==================================================
    # STEP 4 — P3 BICUBIC
    # ==================================================

    print("")
    print("STEP 4: P3 BICUBIC")

    step_start = time.perf_counter()

    bicubic_path = (
        SR_DIR
        / f"{output_name}_bicubic_512.png"
    )

    backend.run_bicubic(
        input_path=str(lr_path),
        output_path=str(bicubic_path),
    )

    print(
        f"[TIME] P3 BICUBIC: "
        f"{time.perf_counter() - step_start:.2f} seconds"
    )

    # --------------------------------------------------
    # Ensure Bicubic = 512x512
    # --------------------------------------------------

    ensure_start = time.perf_counter()

    ensure_512x512(
        bicubic_path
    )

    print(
        f"[TIME] P3 SIZE CHECK: "
        f"{time.perf_counter() - ensure_start:.2f} seconds"
    )

    print(
        f"Bicubic saved to: "
        f"{bicubic_path}"
    )

    # ==================================================
    # STEP 5 — PSNR / SSIM
    # ==================================================

    print("")
    print("STEP 5: PSNR / SSIM")

    evaluation_start = time.perf_counter()

    # --------------------------------------------------
    # Verify HR
    # --------------------------------------------------

    ensure_512x512(
        hr_path
    )

    # --------------------------------------------------
    # ESRGAN metrics
    # --------------------------------------------------

    print("")
    print("Comparing HR vs ESRGAN...")

    sr_metrics = calculate_image_metrics(

        reference_path=str(hr_path),

        reconstructed_path=str(sr_path),
    )

    print(
        f"ESRGAN PSNR: "
        f"{sr_metrics['psnr']:.2f} dB"
    )

    print(
        f"ESRGAN SSIM: "
        f"{sr_metrics['ssim']:.4f}"
    )

    # --------------------------------------------------
    # Bicubic metrics
    # --------------------------------------------------

    print("")
    print("Comparing HR vs Bicubic...")

    bicubic_metrics = calculate_image_metrics(

        reference_path=str(hr_path),

        reconstructed_path=str(
            bicubic_path
        ),
    )

    print(
        f"Bicubic PSNR: "
        f"{bicubic_metrics['psnr']:.2f} dB"
    )

    print(
        f"Bicubic SSIM: "
        f"{bicubic_metrics['ssim']:.4f}"
    )

    print(
        f"[TIME] EVALUATION: "
        f"{time.perf_counter() - evaluation_start:.2f} seconds"
    )

    # ==================================================
    # STEP 6 — P4 SEGMENTATION
    # ==================================================

    print("")
    print("STEP 6: P4 SEGMENTATION")

    p4_start = time.perf_counter()

    p4_path = (
        P4_DIR
        / f"{output_name}_mask.npy"
    )

    p4_result = run_p4_segmentation(

        input_path=str(sr_path),

        output_path=str(p4_path),
    )

    print(
        f"[TIME] P4 SEGMENTATION: "
        f"{time.perf_counter() - p4_start:.2f} seconds"
    )

    # ==================================================
    # STEP 6B — LAND COVER
    # ==================================================

    land_cover_start = time.perf_counter()

    land_cover = calculate_land_cover(
        p4_result
    )

    print(
        f"[TIME] LAND COVER CALCULATION: "
        f"{time.perf_counter() - land_cover_start:.2f} seconds"
    )

    # ==================================================
    # STEP 6C — VISUALIZATION
    # ==================================================

    visualization_start = time.perf_counter()

    p4_visual_path = (
        P4_DIR
        / f"{output_name}_segmentation.png"
    )

    p4_visual_result = (
        create_segmentation_visualization(

            mask_path=p4_result,

            output_path=p4_visual_path,
        )
    )

    print(
        f"[TIME] P4 VISUALIZATION: "
        f"{time.perf_counter() - visualization_start:.2f} seconds"
    )

    # ==================================================
    # STEP 7 — RESULT
    # ==================================================

    pipeline_result = {

        "raw": str(raw_path),

        "hr": str(hr_path),

        "lr": str(lr_path),

        "sr": str(sr_path),

        "bicubic": str(
            bicubic_path
        ),

        "p4": str(
            p4_result
        ),

        "p4_visual": str(
            p4_visual_result
        ),

        "psnr": sr_metrics["psnr"],

        "ssim": sr_metrics["ssim"],

        "bicubic_psnr":
            bicubic_metrics["psnr"],

        "bicubic_ssim":
            bicubic_metrics["ssim"],

        "landCover":
            land_cover,
    }

    # ==================================================
    # FINAL LOG
    # ==================================================

    total_time = (
        time.perf_counter()
        - total_start
    )

    print("")
    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    print(
        f"RAW:       {pipeline_result['raw']}"
    )

    print(
        f"HR:        {pipeline_result['hr']}"
    )

    print(
        f"LR:        {pipeline_result['lr']}"
    )

    print(
        f"SR:        {pipeline_result['sr']}"
    )

    print(
        f"Bicubic:   {pipeline_result['bicubic']}"
    )

    print(
        f"P4 mask:   {pipeline_result['p4']}"
    )

    print(
        f"P4 visual: {pipeline_result['p4_visual']}"
    )

    print("")
    print("Evaluation:")

    print(
        f"  ESRGAN PSNR:  "
        f"{pipeline_result['psnr']:.2f} dB"
    )

    print(
        f"  ESRGAN SSIM:  "
        f"{pipeline_result['ssim']:.4f}"
    )

    print(
        f"  Bicubic PSNR: "
        f"{pipeline_result['bicubic_psnr']:.2f} dB"
    )

    print(
        f"  Bicubic SSIM: "
        f"{pipeline_result['bicubic_ssim']:.4f}"
    )

    print("")
    print("Land-cover:")

    for item in land_cover:

        print(
            f"  {item['label']}: "
            f"{item['share'] * 100:.2f}%"
        )

    # ==================================================
    # TIME SUMMARY
    # ==================================================

    print("")
    print("=" * 60)
    print("TIME SUMMARY")
    print("=" * 60)

    print(
        f"P1 model load/reuse: "
        f"{model_time:.2f} seconds"
    )

    print(
        f"P1 ESRGAN inference: "
        f"{sr_inference_time:.2f} seconds"
    )

    print(
        f"Total pipeline time: "
        f"{total_time:.2f} seconds"
    )

    print("=" * 60)

    return pipeline_result