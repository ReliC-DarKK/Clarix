import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F


# --------------------------------------------------
# P4 PROJECT PATH
# --------------------------------------------------

P4_DIR = Path(__file__).resolve().parent

if str(P4_DIR) not in sys.path:
    sys.path.insert(0, str(P4_DIR))


# --------------------------------------------------
# LOAD P4 MODEL
# --------------------------------------------------

from model import model, processor, DEVICE


EXPECTED_SIZE = 512


# --------------------------------------------------
# P4 CLASS COLORS
# --------------------------------------------------
#
# These IDs must stay consistent with the model's
# predicted class IDs.
#
# 0 = background / other
# 1 = vegetation
# 2 = water
# 3 = agricultural / other
# 4 = barren / other
# 5 = built-up
# 6 = road
# 7 = other
#
# Only the classes currently predicted by the model
# are explicitly highlighted in the frontend.
# --------------------------------------------------

CLASS_COLORS = {
    0: (128, 128, 128),   # background / other
    1: (80, 200, 80),     # vegetation
    2: (30, 120, 220),    # water
    3: (170, 170, 80),    # agricultural / other
    4: (190, 150, 100),   # barren / other
    5: (190, 60, 210),    # built-up
    6: (70, 220, 220),    # road
    7: (160, 160, 160),   # other
}


# --------------------------------------------------
# CREATE COLORED SEGMENTATION IMAGE
# --------------------------------------------------

def create_segmentation_visualization(
    mask: np.ndarray,
    output_path: Path,
):
    """
    Convert the numerical segmentation mask into
    a browser-displayable RGB PNG.

    Input:
        mask: 512x512 class-ID array

    Output:
        Colored 512x512 PNG
    """

    height, width = mask.shape

    visualization = np.zeros(
        (height, width, 3),
        dtype=np.uint8,
    )

    # Paint every class according to CLASS_COLORS.
    for class_id, color in CLASS_COLORS.items():
        visualization[mask == class_id] = color

    # If an unexpected class ID appears, render it
    # as gray instead of silently hiding it.
    known_classes = np.array(
        list(CLASS_COLORS.keys())
    )

    unknown_mask = ~np.isin(
        mask,
        known_classes,
    )

    visualization[unknown_mask] = (
        128,
        128,
        128,
    )

    Image.fromarray(
        visualization,
        mode="RGB",
    ).save(output_path)

    print(
        f"P4 visualization saved to: "
        f"{output_path}"
    )

    return str(output_path)


# --------------------------------------------------
# CALCULATE LAND-COVER SHARES
# --------------------------------------------------

def calculate_land_cover_shares(
    mask: np.ndarray,
):
    """
    Calculate the percentage of pixels belonging
    to the frontend land-cover categories.

    Returns:
        list of dictionaries suitable for the
        Clarix frontend.
    """

    total_pixels = mask.size

    # P4 class -> frontend category
    CLASS_TO_FRONTEND = {
        1: "vegetation",
        2: "water",
        5: "builtup",
        6: "road",
    }

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

    # Count pixels for each predicted class.
    counts = {}

    for class_id in np.unique(mask):
        class_id = int(class_id)

        counts[class_id] = int(
            np.sum(mask == class_id)
        )

    # Calculate frontend shares.
    for item in land_cover:

        frontend_id = item["id"]

        matching_class_ids = [
            class_id
            for class_id, mapped_id
            in CLASS_TO_FRONTEND.items()
            if mapped_id == frontend_id
        ]

        pixel_count = sum(
            counts.get(class_id, 0)
            for class_id in matching_class_ids
        )

        item["share"] = (
            pixel_count / total_pixels
        )

    # "Other" contains everything not mapped to
    # vegetation, water, built-up or road.
    mapped_pixel_count = sum(
        counts.get(class_id, 0)
        for class_id in CLASS_TO_FRONTEND
    )

    other_pixel_count = (
        total_pixels - mapped_pixel_count
    )

    for item in land_cover:
        if item["id"] == "other":
            item["share"] = (
                other_pixel_count / total_pixels
            )

    print("Land-cover shares:")

    for item in land_cover:
        print(
            f"  {item['label']}: "
            f"{item['share'] * 100:.2f}%"
        )

    return land_cover


# --------------------------------------------------
# RUN P4 SEGMENTATION
# --------------------------------------------------

def run_p4(
    input_path: str,
    output_path: str,
):
    """
    Run P4 SegFormer segmentation on a 512x512 image.

    Input:
        P1 SR image

    Outputs:
        1. .npy numerical segmentation mask
        2. .png colored segmentation visualization

    Returns:
        dictionary containing mask path,
        visualization path and land-cover shares.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Starting P4 segmentation...")
    print(f"P4 input: {input_path}")

    if not input_path.exists():
        raise FileNotFoundError(
            f"P4 input image not found: {input_path}"
        )

    # --------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------

    image = Image.open(
        input_path
    ).convert("RGB")

    image_array = np.array(image)

    height, width = image_array.shape[:2]

    print(
        f"P4 input size: "
        f"{width}x{height}"
    )

    # --------------------------------------------------
    # P4 EXPECTS NATIVE 512x512
    # --------------------------------------------------

    if (
        height != EXPECTED_SIZE
        or width != EXPECTED_SIZE
    ):
        raise ValueError(
            f"P4 expected a 512x512 image, "
            f"but received {width}x{height}."
        )

    # --------------------------------------------------
    # PROCESS IMAGE
    # --------------------------------------------------

    inputs = processor(
        images=image,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    # --------------------------------------------------
    # MODEL INFERENCE
    # --------------------------------------------------

    with torch.no_grad():
        outputs = model(**inputs)

    # --------------------------------------------------
    # RESIZE LOGITS BACK TO 512x512
    # --------------------------------------------------

    logits = F.interpolate(
        outputs.logits,
        size=(height, width),
        mode="bilinear",
        align_corners=False,
    )

    # --------------------------------------------------
    # GENERATE SEGMENTATION MASK
    # --------------------------------------------------

    predicted_mask = (
        torch.argmax(
            logits,
            dim=1,
        )[0]
        .cpu()
        .numpy()
        .astype(np.uint8)
    )

    print(
        f"P4 mask size: "
        f"{predicted_mask.shape}"
    )

    predicted_classes = sorted(
        np.unique(
            predicted_mask
        ).tolist()
    )

    print(
        "Predicted classes:",
        predicted_classes,
    )

    # --------------------------------------------------
    # SAVE NUMERICAL MASK
    # --------------------------------------------------

    np.save(
        output_path,
        predicted_mask,
    )

    print(
        f"P4 mask saved to: "
        f"{output_path}"
    )

    # --------------------------------------------------
    # SAVE COLORED PNG
    # --------------------------------------------------

    visualization_path = (
        output_path.parent
        / f"{output_path.stem}_visualization.png"
    )

    create_segmentation_visualization(
        predicted_mask,
        visualization_path,
    )

    # --------------------------------------------------
    # CALCULATE LAND-COVER SHARES
    # --------------------------------------------------

    land_cover = (
        calculate_land_cover_shares(
            predicted_mask
        )
    )

    # --------------------------------------------------
    # RETURN ALL P4 OUTPUTS
    # --------------------------------------------------

    return {
        "mask": str(output_path),
        "visualization": str(
            visualization_path
        ),
        "landCover": land_cover,
        "classes": predicted_classes,
    }


# --------------------------------------------------
# COMPATIBILITY WRAPPER
# --------------------------------------------------

def run_segmentation(
    input_path: str,
    output_dir: str,
):
    """
    Compatibility wrapper for inference_512.py.

    Existing pipeline calls:

        run_segmentation(
            input_path,
            output_directory
        )

    This function keeps that interface while
    also generating the visualization PNG.
    """

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    mask_path = (
        output_dir
        / f"{input_path.stem}_mask.npy"
    )

    result = run_p4(
        input_path=str(input_path),
        output_path=str(mask_path),
    )

    print(
        f"P4 segmentation saved to: "
        f"{result['mask']}"
    )

    print(
        f"P4 visualization saved to: "
        f"{result['visualization']}"
    )

    return result