import cv2
import os
from evaluation_metrics import calculate_psnr, calculate_ssim
import pandas as pd


INPUT_FOLDER = "test_images"
OUTPUT_FOLDER = "visual_results"

results = []

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


for filename in os.listdir(INPUT_FOLDER):

    image_path = os.path.join(INPUT_FOLDER, filename)

    # Skip files that aren't images
    if not filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        continue


    
    # 1. Load the high-resolution image
    hr = cv2.imread(image_path)

    if hr is None:
        print(f"Could not load {filename}")
        continue

    print(f"\nProcessing: {filename}")
    # 2. Calculate 2x downsampled dimensions
    height, width = hr.shape[:2]

    lr_width = width // 2
    lr_height = height // 2

    # 3. Create simulated low-resolution image
    lr = cv2.resize(
        hr,
        (lr_width, lr_height),
        interpolation=cv2.INTER_AREA
    )

    # 4. Upscale using Bicubic
    bicubic = cv2.resize(
        lr,
        (width, height),
        interpolation=cv2.INTER_CUBIC
    )

    # 5. Calculate metrics
    psnr = calculate_psnr(hr, bicubic)
    ssim = calculate_ssim(hr, bicubic)

    # Store results
    results.append({
    "image": filename,
    "psnr": psnr,
    "ssim": ssim
    })

    # Create enlarged LR image for visual comparison
    lr_display = cv2.resize(
    lr,
    (width, height),
    interpolation=cv2.INTER_NEAREST
    )
    # Add labels
    hr_display = hr.copy()
    bicubic_display = bicubic.copy()

    cv2.putText(
        hr_display,
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

    # Combine images side-by-side
    comparison = cv2.hconcat([
        hr_display,
        lr_display,
        bicubic_display
    ])

    # Save comparison
    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"{os.path.splitext(filename)[0]}_comparison.png"
    )

    cv2.imwrite(output_path, comparison)

    print("\n-----------------------------")
    print(f"Image: {filename}")
    print(f"Ground Truth: {hr.shape}")
    print(f"Low Resolution: {lr.shape}")
    print(f"Bicubic Output: {bicubic.shape}")
    print(f"PSNR: {psnr:.4f} dB")
    print(f"SSIM: {ssim:.4f}")

print("\n=============================")
print("BICUBIC BASELINE SUMMARY")
print("=============================")

total_psnr = 0
total_ssim = 0

for result in results:
    print(
        f"{result['image']}: "
        f"PSNR={result['psnr']:.4f} dB, "
        f"SSIM={result['ssim']:.4f}"
    )

    total_psnr += result["psnr"]
    total_ssim += result["ssim"]

if results:
    average_psnr = total_psnr / len(results)
    average_ssim = total_ssim / len(results)

    print("\nAverage PSNR:", f"{average_psnr:.4f} dB")
    print("Average SSIM:", f"{average_ssim:.4f}")

    # Save results to CSV
    results_df = pd.DataFrame(results)

    results_df.to_csv(
        "bicubic_results.csv",
        index=False
    )

    # Save summary to CSV
    summary_df = pd.DataFrame([{
    "average_psnr": average_psnr,
    "average_ssim": average_ssim
    }])

    summary_df.to_csv(
        "bicubic_summary.csv",
        index=False
    )

    print("Summary saved to bicubic_summary.csv")

    print("\nResults saved to bicubic_results.csv")