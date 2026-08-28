import pandas as pd
import matplotlib.pyplot as plt


RESULTS_FILE = "ai_vs_bicubic_results.csv"


df = pd.read_csv(RESULTS_FILE)

if df.empty:
    raise ValueError("The results CSV is empty.")

# Remove the average row for per-patch graphs
plot_df = df[df["patch"] != "AVERAGE"].copy()

# Calculate averages directly from patch results
average_bicubic_psnr = plot_df["bicubic_psnr"].mean()
average_ai_psnr = plot_df["ai_psnr"].mean()

average_bicubic_ssim = plot_df["bicubic_ssim"].mean()
average_ai_ssim = plot_df["ai_ssim"].mean()


# ============================================================
# PSNR COMPARISON
# ============================================================

x = range(len(plot_df))
width = 0.35

plt.figure(figsize=(10, 6))

plt.bar(
    [i - width / 2 for i in x],
    plot_df["bicubic_psnr"],
    width=width,
    label="Bicubic"
)

plt.bar(
    [i + width / 2 for i in x],
    plot_df["ai_psnr"],
    width=width,
    label="AI SR"
)

plt.axhline(
    average_bicubic_psnr,
    linestyle="--",
    label=f"Bicubic Average: {average_bicubic_psnr:.2f} dB"
)

plt.axhline(
    average_ai_psnr,
    linestyle=":",
    label=f"AI Average: {average_ai_psnr:.2f} dB"
)

plt.xlabel("Image")
plt.ylabel("PSNR (dB)")
plt.title("AI Super-Resolution vs Bicubic — PSNR")

plt.xticks(
    list(x),
    plot_df["patch"],
    rotation=45,
    ha="right"
)

plt.legend()
plt.tight_layout()

plt.savefig(
    "ai_vs_bicubic_psnr.png",
    dpi=200
)

plt.show()


# ============================================================
# SSIM COMPARISON
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    [i - width / 2 for i in x],
    plot_df["bicubic_ssim"],
    width=width,
    label="Bicubic"
)

plt.bar(
    [i + width / 2 for i in x],
    plot_df["ai_ssim"],
    width=width,
    label="AI SR"
)

plt.axhline(
    average_bicubic_ssim,
    linestyle="--",
    label=f"Bicubic Average: {average_bicubic_ssim:.4f}"
)

plt.axhline(
    average_ai_ssim,
    linestyle=":",
    label=f"AI Average: {average_ai_ssim:.4f}"
)

plt.xlabel("Image")
plt.ylabel("SSIM")
plt.title("AI Super-Resolution vs Bicubic — SSIM")

plt.xticks(
    list(x),
    plot_df["patch"],
    rotation=45,
    ha="right"
)

plt.legend()
plt.tight_layout()

plt.savefig(
    "ai_vs_bicubic_ssim.png",
    dpi=200
)

plt.show()


# ============================================================
# SUMMARY
# ============================================================

print("\n==============================================")
print("AI vs BICUBIC GRAPH SUMMARY")
print("==============================================")

print(f"Bicubic Average PSNR: {average_bicubic_psnr:.4f} dB")
print(f"AI Average PSNR     : {average_ai_psnr:.4f} dB")

print(f"Bicubic Average SSIM: {average_bicubic_ssim:.4f}")
print(f"AI Average SSIM     : {average_ai_ssim:.4f}")

print("\nGraphs generated successfully.")