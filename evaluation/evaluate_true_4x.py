import cv2
import os
import pandas as pd

from evaluation_metrics import calculate_psnr, calculate_ssim


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

GT_FOLDER = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw"
)

LR_FOLDER = os.path.join(
    PROJECT_ROOT,
    "super_resolution",
    "sat_inputs_128"
)

AI_FOLDER = os.path.join(
    PROJECT_ROOT,
    "super_resolution",
    "sat_outputs_512"
)

OUTPUT_FOLDER = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "true_4x_results"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

results = []


print("=" * 60)
print("FINAL TRUE 4X AI vs BICUBIC EVALUATION")
print("=" * 60)


# ---------------------------------------------------------
# Find matching patches
# ---------------------------------------------------------

patches = []

for filename in os.listdir(GT_FOLDER):

    if not filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        continue

    if not filename.startswith("sentinel_patch_"):
        continue

    patch_number = filename[
        len("sentinel_patch_"):len("sentinel_patch_") + 2
    ]

    gt_path = os.path.join(
        GT_FOLDER,
        filename
    )

    lr_name = (
        f"sentinel_patch_{patch_number}_lr_128.png"
    )

    ai_name = (
        f"sentinel_patch_{patch_number}"
        f"_lr_128_sr_512.png"
    )

    lr_path = os.path.join(
        LR_FOLDER,
        lr_name
    )

    ai_path = os.path.join(
        AI_FOLDER,
        ai_name
    )

    if os.path.exists(lr_path) and os.path.exists(ai_path):

        patches.append(
            (
                patch_number,
                gt_path,
                lr_path,
                ai_path
            )
        )


patches.sort(key=lambda x: x[0])


print(f"Matching patches found: {len(patches)}")

if patches:
    print(
        "Patches: "
        + ", ".join(p[0] for p in patches)
    )

print()


# ---------------------------------------------------------
# Process each patch
# ---------------------------------------------------------

for patch_number, gt_path, lr_path, ai_path in patches:

    print("-" * 60)
    print(f"Processing Patch {patch_number}")
    print("-" * 60)

    gt = cv2.imread(gt_path)
    lr = cv2.imread(lr_path)
    ai = cv2.imread(ai_path)

    if gt is None:
        print("Could not load Ground Truth.")
        continue

    if lr is None:
        print("Could not load LR input.")
        continue

    if ai is None:
        print("Could not load AI output.")
        continue


    # -----------------------------------------------------
    # Verify dimensions
    # -----------------------------------------------------

    gt_height, gt_width = gt.shape[:2]

    if (gt_width, gt_height) != (512, 512):

        print(
            f"WARNING: GT is "
            f"{gt.shape[:2]}, expected (512, 512)"
        )

        continue


    if lr.shape[:2] != (128, 128):

        print(
            f"WARNING: LR is "
            f"{lr.shape[:2]}, expected (128, 128)"
        )

        continue


    if ai.shape[:2] != (512, 512):

        print(
            f"WARNING: AI output is "
            f"{ai.shape[:2]}, expected (512, 512)"
        )

        continue


    # -----------------------------------------------------
    # Bicubic 4x
    # -----------------------------------------------------

    bicubic = cv2.resize(
        lr,
        (512, 512),
        interpolation=cv2.INTER_CUBIC
    )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    bicubic_psnr = calculate_psnr(
        gt,
        bicubic
    )

    ai_psnr = calculate_psnr(
        gt,
        ai
    )

    bicubic_ssim = calculate_ssim(
        gt,
        bicubic
    )

    ai_ssim = calculate_ssim(
        gt,
        ai
    )


    print(f"Ground Truth : {gt.shape}")
    print(f"LR Input     : {lr.shape}")
    print(f"Bicubic 4x   : {bicubic.shape}")
    print(f"AI 4x        : {ai.shape}")

    print()
    print(
        f"Bicubic PSNR: {bicubic_psnr:.4f} dB"
    )

    print(
        f"AI PSNR     : {ai_psnr:.4f} dB"
    )

    print(
        f"Bicubic SSIM: {bicubic_ssim:.4f}"
    )

    print(
        f"AI SSIM     : {ai_ssim:.4f}"
    )


    # -----------------------------------------------------
    # Store results
    # -----------------------------------------------------

    results.append(
        {
            "patch": f"sentinel_patch_{patch_number}",
            "bicubic_psnr": bicubic_psnr,
            "ai_psnr": ai_psnr,
            "bicubic_ssim": bicubic_ssim,
            "ai_ssim": ai_ssim
        }
    )


    # -----------------------------------------------------
    # Visual comparison
    # -----------------------------------------------------

    gt_display = gt.copy()

    lr_display = cv2.resize(
        lr,
        (512, 512),
        interpolation=cv2.INTER_NEAREST
    )

    bicubic_display = bicubic.copy()
    ai_display = ai.copy()


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
        "LR 128x128",
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
        "AI 4x",
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )


    comparison = cv2.hconcat(
        [
            gt_display,
            lr_display,
            bicubic_display,
            ai_display
        ]
    )


    visual_path = os.path.join(
        OUTPUT_FOLDER,
        f"sentinel_patch_{patch_number}_comparison.png"
    )

    cv2.imwrite(
        visual_path,
        comparison
    )


# ---------------------------------------------------------
# Final results
# ---------------------------------------------------------

print()
print("=" * 60)
print("TRUE 4X FINAL RESULTS")
print("=" * 60)


if not results:

    print("No results were generated.")
    print("Check that the GT, LR and AI filenames match.")

    raise SystemExit


results_df = pd.DataFrame(results)


average_row = {
    "patch": "AVERAGE",
    "bicubic_psnr": results_df["bicubic_psnr"].mean(),
    "ai_psnr": results_df["ai_psnr"].mean(),
    "bicubic_ssim": results_df["bicubic_ssim"].mean(),
    "ai_ssim": results_df["ai_ssim"].mean()
}


results_df = pd.concat(
    [
        results_df,
        pd.DataFrame([average_row])
    ],
    ignore_index=True
)


print(
    results_df.to_string(index=False)
)


print()
print("-" * 60)
print("AVERAGE PERFORMANCE")
print("-" * 60)


print(
    f"Bicubic Average PSNR: "
    f"{average_row['bicubic_psnr']:.4f} dB"
)

print(
    f"AI Average PSNR     : "
    f"{average_row['ai_psnr']:.4f} dB"
)

print(
    f"Bicubic Average SSIM: "
    f"{average_row['bicubic_ssim']:.4f}"
)

print(
    f"AI Average SSIM     : "
    f"{average_row['ai_ssim']:.4f}"
)


# ---------------------------------------------------------
# Improvement
# ---------------------------------------------------------

psnr_difference = (
    average_row["ai_psnr"]
    - average_row["bicubic_psnr"]
)

ssim_difference = (
    average_row["ai_ssim"]
    - average_row["bicubic_ssim"]
)


print()
print("-" * 60)
print("AI IMPROVEMENT OVER BICUBIC")
print("-" * 60)


print(
    f"PSNR difference: "
    f"{psnr_difference:+.4f} dB"
)

print(
    f"SSIM difference: "
    f"{ssim_difference:+.4f}"
)


# ---------------------------------------------------------
# Save CSV
# ---------------------------------------------------------

csv_path = os.path.join(
    OUTPUT_FOLDER,
    "true_4x_results.csv"
)

results_df.to_csv(
    csv_path,
    index=False
)


print()
print("Results saved to:")
print(csv_path)

print()
print("Visual comparisons saved to:")
print(OUTPUT_FOLDER)