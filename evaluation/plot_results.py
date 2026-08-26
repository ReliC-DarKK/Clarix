import pandas as pd
import matplotlib.pyplot as plt


# Load the latest Bicubic results
results_file = "bicubic_results.csv"

df = pd.read_csv(results_file)

if df.empty:
    raise ValueError("The results CSV is empty.")

# Calculate averages
average_psnr = df["psnr"].mean()
average_ssim = df["ssim"].mean()


# -----------------------------
# PSNR Graph
# -----------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    df["image"],
    df["psnr"]
)

plt.axhline(
    average_psnr,
    linestyle="--",
    label=f"Average PSNR: {average_psnr:.2f} dB"
)

plt.xlabel("Image")
plt.ylabel("PSNR (dB)")
plt.title("Bicubic Baseline - PSNR")

plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()

plt.savefig(
    "bicubic_psnr_graph.png",
    dpi=200
)

plt.show()


# -----------------------------
# SSIM Graph
# -----------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    df["image"],
    df["ssim"]
)

plt.axhline(
    average_ssim,
    linestyle="--",
    label=f"Average SSIM: {average_ssim:.4f}"
)

plt.xlabel("Image")
plt.ylabel("SSIM")
plt.title("Bicubic Baseline - SSIM")

plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()

plt.savefig(
    "bicubic_ssim_graph.png",
    dpi=200
)

plt.show()


# -----------------------------
# Print summary
# -----------------------------

print("\n=============================")
print("BICUBIC GRAPH SUMMARY")
print("=============================")

print(f"Average PSNR: {average_psnr:.4f} dB")
print(f"Average SSIM: {average_ssim:.4f}")

print("\nGraphs generated successfully.")