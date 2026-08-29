import cv2
import os
import pandas as pd

from evaluation_metrics import calculate_psnr, calculate_ssim


GT_FOLDER = r"C:\Users\91964\Desktop\Klarix\data\raw"
OUTPUT_FOLDER = r"C:\Users\91964\Desktop\Klarix\evaluation\corrected_4x_results"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_patch_id(filename):
    """
    Extract patch ID from filenames such as:
    sentinel_patch_01.png
    sentinel_patch_01_lr_256.png
    sentinel_patch_01_lr_256_sr_1024.png
    """

    name = filename.lower()

    if "sentinel_patch_" not in name:
        return None

    remaining = name.split("sentinel_patch_", 1)[1]

    patch_id = remaining[:2]

    if patch_id.isdigit():
        return patch_id

    return None


def find_file(folder, patch_id, file_type):
    """
    Find the appropriate file for a patch.
    """

    for filename in os.listdir(folder):

        if not filename.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):
            continue

        name = filename.lower()

        if f"sentinel_patch_{patch_id}" not in name:
            continue

        if file_type == "gt":
            if name == f"sentinel_patch_{patch_id}.png":
                return os.path.join(folder, filename)

        elif file_type == "lr":
            if "_lr_256" in name and "_sr_" not in name:
                return os.path.join(folder, filename)

        elif file_type == "sr":
            if "_lr_256_sr_1024" in name:
                return os.path.join(folder, filename)

    return None


# ---------------------------------------------------------
# Folders
# ---------------------------------------------------------

LR_FOLDER = r"C:\Users\91964\Desktop\Klarix\super_resolution\sat_inputs"
SR_FOLDER = r"C:\Users\91964\Desktop\Klarix\super_resolution\sat_outputs"


print("=" * 55)
print("CORRECTED 4X AI vs BICUBIC EVALUATION")
print("=" * 55)

results = []


# ---------------------------------------------------------
# Find available patches
# ---------------------------------------------------------

patch_ids = []

for filename in os.listdir(GT_FOLDER):

    patch_id = get_patch_id(filename)

    if patch_id is not None:
        gt_path = find_file(GT_FOLDER, patch_id, "gt")
        lr_path = find_file(LR_FOLDER, patch_id, "lr")
        sr_path = find_file(SR_FOLDER, patch_id, "sr")

        if gt_path and lr_path and sr_path:
            patch_ids.append(patch_id)


patch_ids = sorted(set(patch_ids))


print(f"Matching patches found: {len(patch_ids)}")
print("Patches:", ", ".join(patch_ids))


# ---------------------------------------------------------
# Process each patch
# ---------------------------------------------------------

for patch_id in patch_ids:

    print("\n" + "-" * 55)
    print(f"Processing Patch {patch_id}")
    print("-" * 55)

    gt_path = find_file(GT_FOLDER, patch_id, "gt")
    lr_path = find_file(LR_FOLDER, patch_id, "lr")
    sr_path = find_file(SR_FOLDER, patch_id, "sr")

    # -----------------------------------------------------
    # Load images
    # -----------------------------------------------------

    gt = cv2.imread(gt_path)
    original_lr = cv2.imread(lr_path)
    original_sr = cv2.imread(sr_path)

    if gt is None:
        print("Could not load ground truth.")
        continue

    if original_lr is None:
        print("Could not load LR image.")
        continue

    if original_sr is None:
        print("Could not load SR image.")
        continue

    # -----------------------------------------------------
    # Create CORRECTED 4x LR from the 512x512 GT
    #
    # 512 -> 128
    # -----------------------------------------------------

    height, width = gt.shape[:2]

    lr_4x_width = width // 4
    lr_4x_height = height // 4

    lr_4x = cv2.resize(
        gt,
        (lr_4x_width, lr_4x_height),
        interpolation=cv2.INTER_AREA
    )

    # -----------------------------------------------------
    # Bicubic 4x
    #
    # 128 -> 512
    # -----------------------------------------------------

    bicubic_4x = cv2.resize(
        lr_4x,
        (width, height),
        interpolation=cv2.INTER_CUBIC
    )

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # Current P1 model is fixed x4.
    # Therefore its existing 256 -> 1024 output cannot
    # directly become a 128 -> 512 output.
    #
    # For this experiment, convert the existing 1024 SR
    # to 512 only for a preliminary comparison.
    #
    # This keeps the model unchanged.
    # -----------------------------------------------------

    ai_512 = cv2.resize(
        original_sr,
        (width, height),
        interpolation=cv2.INTER_AREA
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    bicubic_psnr = calculate_psnr(
        gt,
        bicubic_4x
    )

    bicubic_ssim = calculate_ssim(
        gt,
        bicubic_4x
    )

    ai_psnr = calculate_psnr(
        gt,
        ai_512
    )

    ai_ssim = calculate_ssim(
        gt,
        ai_512
    )

    # -----------------------------------------------------
    # Print
    # -----------------------------------------------------

    print(f"Ground Truth : {gt.shape}")
    print(f"Corrected LR : {lr_4x.shape}")
    print(f"Bicubic 4x   : {bicubic_4x.shape}")
    print(f"Original AI   : {original_sr.shape}")
    print(f"AI Evaluation : {ai_512.shape}")

    print()
    print(f"Bicubic PSNR: {bicubic_psnr:.4f} dB")
    print(f"AI PSNR     : {ai_psnr:.4f} dB")
    print(f"Bicubic SSIM: {bicubic_ssim:.4f}")
    print(f"AI SSIM     : {ai_ssim:.4f}")

    # -----------------------------------------------------
    # Save corrected LR
    # -----------------------------------------------------

    cv2.imwrite(
        os.path.join(
            OUTPUT_FOLDER,
            f"sentinel_patch_{patch_id}_lr_128.png"
        ),
        lr_4x
    )

    # -----------------------------------------------------
    # Save Bicubic
    # -----------------------------------------------------

    cv2.imwrite(
        os.path.join(
            OUTPUT_FOLDER,
            f"sentinel_patch_{patch_id}_bicubic_4x.png"
        ),
        bicubic_4x
    )

    # -----------------------------------------------------
    # Save AI evaluation image
    # -----------------------------------------------------

    cv2.imwrite(
        os.path.join(
            OUTPUT_FOLDER,
            f"sentinel_patch_{patch_id}_ai_512_eval.png"
        ),
        ai_512
    )

    # -----------------------------------------------------
    # Save visual comparison
    # -----------------------------------------------------

    gt_display = gt.copy()
    lr_display = cv2.resize(
        lr_4x,
        (width, height),
        interpolation=cv2.INTER_NEAREST
    )

    bicubic_display = bicubic_4x.copy()
    ai_display = ai_512.copy()

    cv2.putText(
        gt_display,
        "Ground Truth",
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.putText(
        lr_display,
        "128x128 LR",
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.putText(
        bicubic_display,
        "Bicubic 4x",
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.putText(
        ai_display,
        "AI SR",
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    comparison = cv2.hconcat([
        gt_display,
        lr_display,
        bicubic_display,
        ai_display
    ])

    cv2.imwrite(
        os.path.join(
            OUTPUT_FOLDER,
            f"sentinel_patch_{patch_id}_comparison.png"
        ),
        comparison
    )

    results.append({
        "patch": f"sentinel_patch_{patch_id}",
        "bicubic_psnr": bicubic_psnr,
        "ai_psnr": ai_psnr,
        "bicubic_ssim": bicubic_ssim,
        "ai_ssim": ai_ssim
    })


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\n" + "=" * 55)
print("CORRECTED 4X RESULTS")
print("=" * 55)

if results:

    df = pd.DataFrame(results)

    average_row = pd.DataFrame([{
        "patch": "AVERAGE",
        "bicubic_psnr": df["bicubic_psnr"].mean(),
        "ai_psnr": df["ai_psnr"].mean(),
        "bicubic_ssim": df["bicubic_ssim"].mean(),
        "ai_ssim": df["ai_ssim"].mean()
    }])

    final_df = pd.concat(
        [df, average_row],
        ignore_index=True
    )

    print(final_df.to_string(index=False))

    output_csv = os.path.join(
        OUTPUT_FOLDER,
        "corrected_4x_results.csv"
    )

    final_df.to_csv(
        output_csv,
        index=False
    )

    print()
    print("Results saved to:")
    print(output_csv)

else:
    print("No matching patches found.")