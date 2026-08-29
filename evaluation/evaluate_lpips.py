import os
import cv2
import torch
import lpips
import pandas as pd
from PIL import Image


# =========================================================
# PROJECT PATHS
# =========================================================

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
    "lpips_results"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# =========================================================
# DEVICE
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("LPIPS PERCEPTUAL BASELINE")
print("=" * 60)

print(f"Device: {device}")
print()


# =========================================================
# LOAD LPIPS MODEL
# =========================================================

print("Loading LPIPS model...")

loss_fn = lpips.LPIPS(
    net="alex"
).to(device)

loss_fn.eval()

print("LPIPS model loaded.")
print()


# =========================================================
# HELPER FUNCTION
# =========================================================

def image_to_tensor(image_path):
    """
    Load image and convert it to the format expected by LPIPS.

    LPIPS expects:
        RGB
        float32
        range [-1, 1]
        shape [1, 3, H, W]
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = (
        torch.from_numpy(
            __import__("numpy").array(image)
        )
        .permute(2, 0, 1)
        .float()
        / 255.0
    )

    tensor = (
        tensor * 2.0
    ) - 1.0

    tensor = tensor.unsqueeze(0)

    return tensor.to(device)


# =========================================================
# FIND MATCHING PATCHES
# =========================================================

patches = []

for filename in os.listdir(GT_FOLDER):

    if not filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        continue

    if not filename.startswith(
        "sentinel_patch_"
    ):
        continue

    patch_number = filename[
        len("sentinel_patch_"):
        len("sentinel_patch_") + 2
    ]

    gt_path = os.path.join(
        GT_FOLDER,
        filename
    )

    lr_path = os.path.join(
        LR_FOLDER,
        f"sentinel_patch_{patch_number}_lr_128.png"
    )

    ai_path = os.path.join(
        AI_FOLDER,
        f"sentinel_patch_{patch_number}_lr_128_sr_512.png"
    )

    if (
        os.path.exists(gt_path)
        and os.path.exists(lr_path)
        and os.path.exists(ai_path)
    ):

        patches.append(
            (
                patch_number,
                gt_path,
                lr_path,
                ai_path
            )
        )


patches.sort(
    key=lambda x: x[0]
)


print(
    f"Matching patches found: {len(patches)}"
)

if patches:

    print(
        "Patches: "
        + ", ".join(
            p[0] for p in patches
        )
    )

print()


# =========================================================
# PROCESS PATCHES
# =========================================================

results = []


for (
    patch_number,
    gt_path,
    lr_path,
    ai_path
) in patches:

    print("-" * 60)
    print(
        f"Processing Patch {patch_number}"
    )
    print("-" * 60)


    # -----------------------------------------------------
    # Load images
    # -----------------------------------------------------

    gt = cv2.imread(
        gt_path
    )

    lr = cv2.imread(
        lr_path
    )

    ai = cv2.imread(
        ai_path
    )


    if gt is None:
        print("Could not load Ground Truth.")
        continue

    if lr is None:
        print("Could not load LR.")
        continue

    if ai is None:
        print("Could not load AI.")
        continue


    # -----------------------------------------------------
    # Verify dimensions
    # -----------------------------------------------------

    print(
        f"Ground Truth : {gt.shape}"
    )

    print(
        f"LR Input     : {lr.shape}"
    )

    print(
        f"AI Output    : {ai.shape}"
    )


    if gt.shape[:2] != (512, 512):

        print(
            "ERROR: Ground Truth is not 512x512."
        )

        continue


    if lr.shape[:2] != (128, 128):

        print(
            "ERROR: LR is not 128x128."
        )

        continue


    if ai.shape[:2] != (512, 512):

        print(
            "ERROR: AI output is not 512x512."
        )

        continue


    # -----------------------------------------------------
    # Generate Bicubic 4x
    # -----------------------------------------------------

    bicubic = cv2.resize(
        lr,
        (512, 512),
        interpolation=cv2.INTER_CUBIC
    )


    # -----------------------------------------------------
    # Save temporary comparison images
    # -----------------------------------------------------

    bicubic_path = os.path.join(
        OUTPUT_FOLDER,
        f"sentinel_patch_{patch_number}_bicubic.png"
    )

    cv2.imwrite(
        bicubic_path,
        bicubic
    )


    # -----------------------------------------------------
    # Convert images to LPIPS tensors
    # -----------------------------------------------------

    gt_tensor = image_to_tensor(
        gt_path
    )

    bicubic_tensor = image_to_tensor(
        bicubic_path
    )

    ai_tensor = image_to_tensor(
        ai_path
    )


    # -----------------------------------------------------
    # Calculate LPIPS
    # -----------------------------------------------------

    with torch.no_grad():

        bicubic_lpips = loss_fn(
            gt_tensor,
            bicubic_tensor
        ).item()

        ai_lpips = loss_fn(
            gt_tensor,
            ai_tensor
        ).item()


    print()
    print(
        f"Bicubic LPIPS: {bicubic_lpips:.6f}"
    )

    print(
        f"AI LPIPS     : {ai_lpips:.6f}"
    )


    # -----------------------------------------------------
    # Interpretation
    # -----------------------------------------------------

    if ai_lpips < bicubic_lpips:

        print(
            "AI perceptual distance: BETTER"
        )

    elif ai_lpips > bicubic_lpips:

        print(
            "Bicubic perceptual distance: BETTER"
        )

    else:

        print(
            "Perceptual distance: EQUAL"
        )


    # -----------------------------------------------------
    # Store results
    # -----------------------------------------------------

    results.append(
        {
            "patch":
                f"sentinel_patch_{patch_number}",

            "bicubic_lpips":
                bicubic_lpips,

            "ai_lpips":
                ai_lpips,

            "ai_lpips_difference":
                ai_lpips - bicubic_lpips
        }
    )


# =========================================================
# FINAL RESULTS
# =========================================================

print()
print("=" * 60)
print("LPIPS FINAL RESULTS")
print("=" * 60)


if not results:

    print(
        "No results were generated."
    )

    raise SystemExit


results_df = pd.DataFrame(
    results
)


# =========================================================
# AVERAGE
# =========================================================

average_bicubic = (
    results_df[
        "bicubic_lpips"
    ].mean()
)

average_ai = (
    results_df[
        "ai_lpips"
    ].mean()
)

average_difference = (
    average_ai
    - average_bicubic
)


average_row = {

    "patch":
        "AVERAGE",

    "bicubic_lpips":
        average_bicubic,

    "ai_lpips":
        average_ai,

    "ai_lpips_difference":
        average_difference
}


results_df = pd.concat(
    [
        results_df,

        pd.DataFrame(
            [average_row]
        )
    ],

    ignore_index=True
)


print(
    results_df.to_string(
        index=False
    )
)


# =========================================================
# INTERPRETATION
# =========================================================

print()
print("-" * 60)
print("AVERAGE PERCEPTUAL PERFORMANCE")
print("-" * 60)

print(
    f"Bicubic Average LPIPS: "
    f"{average_bicubic:.6f}"
)

print(
    f"AI Average LPIPS     : "
    f"{average_ai:.6f}"
)

print(
    f"AI - Bicubic         : "
    f"{average_difference:+.6f}"
)


print()

if average_ai < average_bicubic:

    print(
        "RESULT: AI has LOWER LPIPS."
    )

    print(
        "This indicates that AI is "
        "perceptually closer to the "
        "ground truth than Bicubic."
    )

elif average_ai > average_bicubic:

    print(
        "RESULT: Bicubic has LOWER LPIPS."
    )

    print(
        "This indicates that Bicubic is "
        "perceptually closer to the "
        "ground truth than AI."
    )

else:

    print(
        "RESULT: AI and Bicubic have "
        "equal average LPIPS."
    )


# =========================================================
# SAVE CSV
# =========================================================

csv_path = os.path.join(
    OUTPUT_FOLDER,
    "lpips_results.csv"
)

results_df.to_csv(
    csv_path,
    index=False
)


print()
print(
    "Results saved to:"
)

print(
    csv_path
)

print()
print(
    "LPIPS baseline complete."
)