"""
inference_512.py

Experimental P4 SegFormer inference script for the NEW P1 pipeline:

    128x128 LR -> 4x ESRGAN -> native 512x512 SR -> P4 SegFormer

This script is intentionally isolated from inference.py so the existing
(working) inference behavior is never modified. It:

  1. Runs inference on the original 512x512 satellite images
     (test-images/original/) as a baseline.
  2. Runs inference on the NEW native 512x512 SR images produced by
     P1's updated 128->512 ESRGAN pipeline (test-images/super-res/).

No 1024->512 (or 512->1024->512) resizing is performed anywhere in this
script -- the SR images are expected to already be native 512x512, and
any mismatch is reported, not silently corrected.

Masks are written to:
    test-images/results/original/
    test-images/results/super-res/

NOTE: the new native 128->512 SR images go in test-images/super-res-512/
(a separate folder from test-images/super-res/, which still holds the
old 256->1024 pipeline's output). This keeps the two experiments'
inputs and result masks from mixing.

Usage:
    python inference_512.py
"""

import os
import glob
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

from model import model, processor, DEVICE

# ---------------------------------------------------------------------------
# Fixed pipeline constants (per project spec -- printed for logging only,
# do not change)
# ---------------------------------------------------------------------------
MODEL_NAME = "wu-pr-gw/segformer-b2-finetuned-with-LoveDA"
CHECKPOINT_PATH = os.path.join("weights", "segformer_loveda_epoch_6.pth")

ORIGINAL_DIR = os.path.join("Mapping-Segmentation", "test-images", "original")
# New native 128->512 SR images live in their own folder, separate from
# the old 256->1024 pipeline's output in test-images/super-res/.
SUPER_RES_DIR = os.path.join("Mapping-Segmentation", "test-images", "super_res_512")

RESULTS_ORIGINAL_DIR = os.path.join("Mapping-Segmentation", "test-images", "results", "original")
RESULTS_SUPER_RES_DIR = os.path.join("Mapping-Segmentation", "test-images", "results", "super_res_512")

EXPECTED_SIZE = 512  # expected width == height for this experiment

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")


def list_images(directory):
    """Return a sorted list of image paths in `directory` (empty if missing)."""
    if not os.path.isdir(directory):
        return []
    files = []
    for ext in IMAGE_EXTENSIONS:
        files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
        files.extend(glob.glob(os.path.join(directory, f"*{ext.upper()}")))
    return sorted(set(files))


def run_segmentation(image_path, results_dir):
    """
    Run P4 SegFormer inference on a single image and save the predicted
    mask as a .npy file (named "<stem>_mask.npy"). Returns the saved
    mask path, or None if the image could not be processed.
    """
    filename = os.path.basename(image_path)
    stem, _ = os.path.splitext(filename)

    print(f"\nInput image: {filename}")

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as exc:
        print(f"  [ERROR] Could not open image: {exc}")
        return None

    image_array = np.array(image)
    h, w = image_array.shape[0], image_array.shape[1]

    print(f"Input image shape: {image_array.shape}")

    if h != EXPECTED_SIZE or w != EXPECTED_SIZE:
        print(
            f"  [WARNING] Expected {EXPECTED_SIZE}x{EXPECTED_SIZE} but got "
            f"{w}x{h}. This mismatch is NOT silently corrected -- "
            f"investigate the upstream P1 output for this image."
        )

    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = F.interpolate(
        outputs.logits,
        size=image_array.shape[:2],
        mode="bilinear",
        align_corners=False,
    )

    predicted_mask = torch.argmax(logits, dim=1)[0].cpu().numpy().astype(np.uint8)

    print(f"Output mask shape: {predicted_mask.shape}")
    unique_classes = sorted(np.unique(predicted_mask).tolist())
    print(f"Predicted classes: {unique_classes}")

    os.makedirs(results_dir, exist_ok=True)
    mask_path = os.path.join(results_dir, f"{stem}_mask.npy")
    np.save(mask_path, predicted_mask)

    return mask_path


def main():
    print("=" * 70)
    print("P4 SEGFORMER 512x512 SR EXPERIMENT")
    print("=" * 70)
    print(f"Model: {MODEL_NAME}")
    print(f"Checkpoint: {CHECKPOINT_PATH}")
    print(f"Device: {DEVICE}")
    print(f"Processor size: {getattr(processor, 'size', 'unknown')}")

    saved_masks = []

    print("\n" + "-" * 70)
    print("ORIGINAL IMAGE INFERENCE")
    print("-" * 70)
    original_images = list_images(ORIGINAL_DIR)
    if not original_images:
        print(f"  [WARNING] No images found in {ORIGINAL_DIR}")
    for image_path in original_images:
        mask_path = run_segmentation(image_path, RESULTS_ORIGINAL_DIR)
        if mask_path:
            saved_masks.append(mask_path)

    print("\n" + "-" * 70)
    print("NATIVE 512x512 SR IMAGE INFERENCE")
    print("-" * 70)
    sr_images = list_images(SUPER_RES_DIR)
    if not sr_images:
        print(f"  [WARNING] No images found in {SUPER_RES_DIR}")
    for image_path in sr_images:
        mask_path = run_segmentation(image_path, RESULTS_SUPER_RES_DIR)
        if mask_path:
            saved_masks.append(mask_path)

    print("\n" + "=" * 70)
    print("DONE -- generated masks:")
    print("=" * 70)
    for path in saved_masks:
        print(f"  {path}")

    print(f"\nOriginal masks dir: {RESULTS_ORIGINAL_DIR}")
    print(f"SR masks dir:       {RESULTS_SUPER_RES_DIR}")


if __name__ == "__main__":
    main()
