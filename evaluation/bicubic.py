import cv2
import os
import pandas as pd

from evaluation_metrics import calculate_psnr, calculate_ssim


# ============================================================
# PROJECT PATHS
# ============================================================

GT_FOLDER = r"C:\Users\91964\Desktop\Klarix\data\raw"

LR_FOLDER = r"C:\Users\91964\Desktop\Klarix\super_resolution\sat_inputs"

SR_FOLDER = r"C:\Users\91964\Desktop\Klarix\super_resolution\sat_outputs"

OUTPUT_FOLDER = "final_visual_results"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# FIND PATCH NUMBER
# ============================================================

def get_patch_number(filename):
    """
    Extract patch number from filenames such as:

    sentinel_patch_01.png
    sentinel_patch_01_lr_256.png
    sentinel_patch_01_lr_256_sr_1024.png
    """

    parts = filename.lower().split("patch_")

    if len(parts) < 2:
        return None

    number = parts[1].split("_")[0].split(".")[0]

    return number


# ============================================================
# BUILD FILE MAPS
# ============================================================

gt_files = {}
lr_files = {}
sr_files = {}


for filename in os.listdir(GT_FOLDER):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        patch = get_patch_number(filename)

        if patch:
            gt_files[patch] = os.path.join(GT_FOLDER, filename)


for filename in os.listdir(LR_FOLDER):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        patch = get_patch_number(filename)

        if patch:
            lr_files[patch] = os.path.join(LR_FOLDER, filename)


for filename in os.listdir(SR_FOLDER):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        patch = get_patch_number(filename)

        if patch:
            sr_files[patch] = os.path.join(SR_FOLDER, filename)


# ============================================================
# FIND COMMON PATCHES
# ============================================================

patches = sorted(
    set(gt_files) &
    set(lr_files) &
    set(sr_files),
    key=lambda x: int(x)
)


if not patches:
    raise ValueError(
        "No matching patches were found between GT, LR and SR folders."
    )


print("\n==============================================")
print("FINAL AI vs BICUBIC EVALUATION")
print("==============================================")

print(f"Matching patches found: {len(patches)}")
print("Patches:", ", ".join(patches))


# ============================================================
# PROCESS EACH PATCH
# ============================================================

results = []


for patch in patches:

    print("\n----------------------------------------------")
    print(f"Processing Patch {patch}")
    print("----------------------------------------------")

    # --------------------------------------------------------
    # Load images
    # --------------------------------------------------------

    gt = cv2.imread(gt_files[patch])
    lr = cv2.imread(lr_files[patch])
    sr = cv2.imread(sr_files[patch])

    if gt is None:
        print("Could not load ground truth.")
        continue

    if lr is None:
        print("Could not load LR image.")
        continue

    if sr is None:
        print("Could not load SR image.")
        continue


    # --------------------------------------------------------
    # Ground Truth dimensions
    # --------------------------------------------------------

    gt_height, gt_width = gt.shape[:2]


    # --------------------------------------------------------
    # Bicubic reconstruction
    #
    # 256 × 256 → 512 × 512
    # --------------------------------------------------------

    bicubic = cv2.resize(
        lr,
        (gt_width, gt_height),
        interpolation=cv2.INTER_CUBIC
    )


    # --------------------------------------------------------
    # Resize AI SR output for evaluation
    #
    # 1024 × 1024 → 512 × 512
    #
    # This resized copy is ONLY used for PSNR/SSIM.
    # The original 1024 × 1024 SR image is preserved.
    # --------------------------------------------------------

    sr_eval = cv2.resize(
        sr,
        (gt_width, gt_height),
        interpolation=cv2.INTER_AREA
    )


    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------

    bicubic_psnr = calculate_psnr(
        gt,
        bicubic
    )

    bicubic_ssim = calculate_ssim(
        gt,
        bicubic
    )

    ai_psnr = calculate_psnr(
        gt,
        sr_eval
    )

    ai_ssim = calculate_ssim(
        gt,
        sr_eval
    )


    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    results.append({
        "patch": f"sentinel_patch_{patch}",
        "bicubic_psnr": bicubic_psnr,
        "ai_psnr": ai_psnr,
        "bicubic_ssim": bicubic_ssim,
        "ai_ssim": ai_ssim
    })


    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print(f"Ground Truth : {gt.shape}")
    print(f"LR Input     : {lr.shape}")
    print(f"Bicubic      : {bicubic.shape}")
    print(f"AI SR        : {sr.shape}")
    print(f"AI Evaluation: {sr_eval.shape}")

    print(f"\nBicubic PSNR: {bicubic_psnr:.4f} dB")
    print(f"AI PSNR     : {ai_psnr:.4f} dB")

    print(f"Bicubic SSIM: {bicubic_ssim:.4f}")
    print(f"AI SSIM     : {ai_ssim:.4f}")


    # ========================================================
    # VISUAL COMPARISON
    # ========================================================

    # Enlarge LR only for visualization
    lr_display = cv2.resize(
        lr,
        (gt_width, gt_height),
        interpolation=cv2.INTER_NEAREST
    )

    # Resize AI output only for visualization
    ai_display = cv2.resize(
        sr,
        (gt_width, gt_height),
        interpolation=cv2.INTER_AREA
    )

    # Copies for labels
    gt_display = gt.copy()
    bicubic_display = bicubic.copy()

    cv2.putText(
        gt_display,
        "Ground Truth",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        lr_display,
        "LR Input",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        bicubic_display,
        "Bicubic",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        ai_display,
        "AI SR",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


    comparison = cv2.hconcat([
        gt_display,
        lr_display,
        bicubic_display,
        ai_display
    ])


    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"sentinel_patch_{patch}_comparison.png"
    )

    cv2.imwrite(
        output_path,
        comparison
    )


# ============================================================
# CREATE FINAL RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)


if results_df.empty:
    raise ValueError("No evaluation results were generated.")


# ============================================================
# AVERAGES
# ============================================================

average_bicubic_psnr = results_df["bicubic_psnr"].mean()
average_ai_psnr = results_df["ai_psnr"].mean()

average_bicubic_ssim = results_df["bicubic_ssim"].mean()
average_ai_ssim = results_df["ai_ssim"].mean()


# Add average row
average_row = pd.DataFrame([{
    "patch": "AVERAGE",
    "bicubic_psnr": average_bicubic_psnr,
    "ai_psnr": average_ai_psnr,
    "bicubic_ssim": average_bicubic_ssim,
    "ai_ssim": average_ai_ssim
}])


final_results = pd.concat(
    [results_df, average_row],
    ignore_index=True
)


# ============================================================
# SAVE FINAL CSV
# ============================================================

final_results.to_csv(
    "ai_vs_bicubic_results.csv",
    index=False
)


# ============================================================
# PRINT FINAL SUMMARY
# ============================================================

print("\n==============================================")
print("FINAL RESULTS")
print("==============================================")

print(final_results.to_string(index=False))

print("\n----------------------------------------------")
print("AVERAGE PERFORMANCE")
print("----------------------------------------------")

print(
    f"Bicubic Average PSNR: "
    f"{average_bicubic_psnr:.4f} dB"
)

print(
    f"AI Average PSNR     : "
    f"{average_ai_psnr:.4f} dB"
)

print(
    f"Bicubic Average SSIM: "
    f"{average_bicubic_ssim:.4f}"
)

print(
    f"AI Average SSIM     : "
    f"{average_ai_ssim:.4f}"
)

print("\nResults saved to:")
print("ai_vs_bicubic_results.csv")

print("\nVisual comparisons saved to:")
print(OUTPUT_FOLDER)