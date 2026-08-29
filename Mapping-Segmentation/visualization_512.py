"""
visualization_512.py

Builds 2x2 comparison images between:

    Original 512x512 image      vs   Native 512x512 SR image (new P1 pipeline)
    Original segmentation        vs   SR segmentation

Each comparison also includes:
  - A colored frame around the "Original" column and a separately
    colored frame around the "Super-Resolved" column, with a visible
    gap between them, so the two sides are easy to tell apart at a
    glance.
  - A class-color legend strip along the bottom, built from the
    existing CLASS_COLORS mapping (class names added only for the
    legend labels -- class IDs/colors themselves are unchanged).

This is an isolated experiment for P1's new 128->512 ESRGAN pipeline.
It does not modify visualization.py, and it does not perform any
1024->512 or 512->1024->512 resizing -- SR images are expected to
already be native 512x512 (images are only resized, if at all, to fit
the comparison canvas).

Requires that inference_512.py has already been run, since this script
reads the .npy masks it produces.

Output:
    Mapping-Segmentation/test-images/results/comparisons_512/<patch_id>_comparison.png

    e.g. sentinel_patch_01_comparison.png

Usage:
    python visualization_512.py
"""

import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ORIGINAL_DIR = os.path.join("Mapping-Segmentation", "test-images", "original")
# New native 128->512 SR images live in their own folder, separate from
# the old 256->1024 pipeline's output in test-images/super-res/.
SUPER_RES_DIR = os.path.join("Mapping-Segmentation", "test-images", "super_res_512")

RESULTS_ORIGINAL_DIR = os.path.join("Mapping-Segmentation", "test-images", "results", "original")
RESULTS_SUPER_RES_DIR = os.path.join("Mapping-Segmentation", "test-images", "results", "super_res_512")

OUTPUT_DIR = os.path.join("Mapping-Segmentation", "test-images", "results", "comparisons_512")

TILE_SIZE = 512          # each panel's image area, in pixels
LABEL_HEIGHT = 30        # header strip above each panel
FRAME_WIDTH = 6          # thickness of the colored column frame
COLUMN_GAP = 24          # visible gap between the Original and SR columns
OUTER_PADDING = 16       # padding around the whole canvas
LEGEND_HEIGHT = 50       # height of the class-color legend strip

ORIGINAL_FRAME_COLOR = (70, 130, 180)     # steel blue
SR_FRAME_COLOR = (230, 126, 34)           # orange

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

# Existing P4 class colors -- unchanged, do not add/remove classes here.
CLASS_COLORS = {
    0: (0, 0, 0),
    1: (128, 128, 128),
    2: (255, 0, 0),
    3: (255, 255, 0),
    4: (0, 0, 255),
    5: (139, 69, 19),
    6: (0, 128, 0),
    7: (255, 165, 0),
}

# Class names, in the same order/IDs as CLASS_COLORS, used only for the
# legend labels -- does not affect segmentation logic or class IDs.
CLASS_NAMES = {
    0: "Ignore",
    1: "Background",
    2: "Building",
    3: "Road",
    4: "Water",
    5: "Barren",
    6: "Forest",
    7: "Agriculture",
}

# Matches the shared patch identifier in both original and SR filenames,
# e.g. "sentinel_patch_01" out of "sentinel_patch_01_lr_128_sr_512.png"
PATCH_ID_PATTERN = re.compile(r"(sentinel_patch_\d+)")


def find_patch_id(filename):
    match = PATCH_ID_PATTERN.search(filename)
    return match.group(1) if match else None


def find_sr_image_for_patch(patch_id):
    """
    Find the SR file in test-images/super_res_512/ whose name contains
    patch_id.

    test-images/super_res_512/ is meant to hold only the new native
    128->512 pipeline's output, so normally there's exactly one match per
    patch_id. This still guards against accidental duplicates (e.g. two
    uploads of the same patch) by preferring filenames that look like the
    new pipeline ("128" and/or "512" in the name), warning if it has to
    choose, and falling back to the most recently modified file rather
    than silently guessing.
    """
    if not os.path.isdir(SUPER_RES_DIR):
        return None

    candidates = sorted(
        f for f in os.listdir(SUPER_RES_DIR)
        if patch_id in f and f.lower().endswith(IMAGE_EXTENSIONS)
    )
    if not candidates:
        return None
    if len(candidates) == 1:
        return os.path.join(SUPER_RES_DIR, candidates[0])

    new_pipeline_candidates = [
        f for f in candidates if ("128" in f or "sr_512" in f or "_512" in f)
    ]
    old_pipeline_candidates = [
        f for f in candidates if ("256" in f or "1024" in f)
    ]

    print(f"  [WARNING] Multiple SR files found for {patch_id}: {candidates}")

    if new_pipeline_candidates and not old_pipeline_candidates == candidates:
        chosen = sorted(new_pipeline_candidates)[0]
        print(f"    -> Using new-pipeline-looking file: {chosen}")
        return os.path.join(SUPER_RES_DIR, chosen)

    # No clear "new pipeline" naming signal -- fall back to most recently
    # modified file and say so explicitly, rather than silently picking
    # whatever sorts first alphabetically.
    candidates_full = [os.path.join(SUPER_RES_DIR, f) for f in candidates]
    chosen = max(candidates_full, key=os.path.getmtime)
    print(f"    -> No clear new-pipeline filename match; using most "
          f"recently modified file: {os.path.basename(chosen)}")
    return chosen


def find_mask_for_stem(stem, results_dir):
    mask_path = os.path.join(results_dir, f"{stem}_mask.npy")
    return mask_path if os.path.isfile(mask_path) else None


def colorize_mask(mask_array):
    h, w = mask_array.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)
    for class_id, color in CLASS_COLORS.items():
        color_mask[mask_array == class_id] = color
    return Image.fromarray(color_mask)


def make_labeled_tile(image, label, size=TILE_SIZE):
    image = image.convert("RGB")
    if image.size != (size, size):
        # Only resized to fit the comparison canvas -- not an
        # experimental resolution conversion.
        image = image.resize((size, size), Image.NEAREST)

    tile = Image.new("RGB", (size, size + LABEL_HEIGHT), (255, 255, 255))
    tile.paste(image, (0, LABEL_HEIGHT))

    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()
    draw.text((5, 5), label, fill=(0, 0, 0), font=font)
    return tile


def make_framed_column(top_tile, bottom_tile, frame_color, frame_width=FRAME_WIDTH):
    """Stack two tiles vertically and draw a colored frame/border around them."""
    col_w = top_tile.width
    col_h = top_tile.height + bottom_tile.height

    framed = Image.new(
        "RGB",
        (col_w + 2 * frame_width, col_h + 2 * frame_width),
        frame_color,
    )
    framed.paste(top_tile, (frame_width, frame_width))
    framed.paste(bottom_tile, (frame_width, frame_width + top_tile.height))
    return framed


def make_legend(width, height=LEGEND_HEIGHT):
    """Build a horizontal legend strip showing each class's color and name."""
    legend = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(legend)
    font = ImageFont.load_default()

    swatch_size = 16
    padding_x = 12
    y = (height - swatch_size) // 2

    x = padding_x
    for class_id in sorted(CLASS_COLORS.keys()):
        color = CLASS_COLORS[class_id]
        name = CLASS_NAMES.get(class_id, str(class_id))

        draw.rectangle([x, y, x + swatch_size, y + swatch_size], fill=color, outline=(0, 0, 0))
        text = f"{class_id}: {name}"
        draw.text((x + swatch_size + 4, y + 1), text, fill=(0, 0, 0), font=font)

        text_width = draw.textlength(text, font=font)
        x += swatch_size + 4 + text_width + padding_x * 2

    return legend


def build_comparison(original_img_path, sr_img_path, original_mask_path, sr_mask_path, out_path):
    original_img = Image.open(original_img_path).convert("RGB")
    sr_img = Image.open(sr_img_path).convert("RGB")

    original_mask = np.load(original_mask_path)
    sr_mask = np.load(sr_mask_path)

    original_seg_img = colorize_mask(original_mask)
    sr_seg_img = colorize_mask(sr_mask)

    tile_tl = make_labeled_tile(original_img, "Original")
    tile_tr = make_labeled_tile(sr_img, "Super-Resolved (512x512)")
    tile_bl = make_labeled_tile(original_seg_img, "Original Segmentation")
    tile_br = make_labeled_tile(sr_seg_img, "SR Segmentation")

    left_column = make_framed_column(tile_tl, tile_bl, ORIGINAL_FRAME_COLOR)
    right_column = make_framed_column(tile_tr, tile_br, SR_FRAME_COLOR)

    col_w, col_h = left_column.size
    content_w = col_w * 2 + COLUMN_GAP
    canvas_w = content_w + 2 * OUTER_PADDING
    canvas_h = col_h + 2 * OUTER_PADDING + LEGEND_HEIGHT

    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    canvas.paste(left_column, (OUTER_PADDING, OUTER_PADDING))
    canvas.paste(right_column, (OUTER_PADDING + col_w + COLUMN_GAP, OUTER_PADDING))

    legend = make_legend(content_w)
    canvas.paste(legend, (OUTER_PADDING, OUTER_PADDING + col_h))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)


def main():
    print("=" * 70)
    print("P4 512x512 SR COMPARISON VISUALIZATION")
    print("=" * 70)

    if not os.path.isdir(ORIGINAL_DIR):
        print(f"[ERROR] Original image directory not found: {ORIGINAL_DIR}")
        return

    original_images = sorted(
        f for f in os.listdir(ORIGINAL_DIR) if f.lower().endswith(IMAGE_EXTENSIONS)
    )

    if not original_images:
        print(f"[WARNING] No original images found in {ORIGINAL_DIR}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    created = []

    for original_filename in original_images:
        patch_id = find_patch_id(original_filename)
        if patch_id is None:
            print(f"\n[SKIP] Could not extract patch id from: {original_filename}")
            continue

        print(f"\nPatch: {patch_id}")

        original_img_path = os.path.join(ORIGINAL_DIR, original_filename)
        sr_img_path = find_sr_image_for_patch(patch_id)

        original_stem, _ = os.path.splitext(original_filename)
        original_mask_path = find_mask_for_stem(original_stem, RESULTS_ORIGINAL_DIR)

        sr_mask_path = None
        if sr_img_path:
            sr_stem, _ = os.path.splitext(os.path.basename(sr_img_path))
            sr_mask_path = find_mask_for_stem(sr_stem, RESULTS_SUPER_RES_DIR)

        # -------- validation: skip (don't crash) on any missing piece --------
        missing = []
        if not os.path.isfile(original_img_path):
            missing.append("original image")
        if not sr_img_path:
            missing.append("SR image")
        if not original_mask_path:
            missing.append("original mask")
        if not sr_mask_path:
            missing.append("SR mask")

        if missing:
            print(
                f"  [SKIP] Missing: {', '.join(missing)}. "
                f"Run inference_512.py first if masks are missing."
            )
            continue

        out_path = os.path.join(OUTPUT_DIR, f"{patch_id}_comparison.png")
        try:
            build_comparison(
                original_img_path, sr_img_path,
                original_mask_path, sr_mask_path,
                out_path,
            )
        except Exception as exc:
            print(f"  [ERROR] Failed to build comparison for {patch_id}: {exc}")
            continue

        print(f"  [OK] Saved: {out_path}")
        created.append(out_path)

    print("\n" + "=" * 70)
    print(f"Created {len(created)} comparison image(s) in: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
