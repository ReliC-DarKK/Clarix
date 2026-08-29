import cv2
import os


GT_FOLDER = r"C:\Users\91964\Desktop\Klarix\data\raw"
OUTPUT_FOLDER = r"C:\Users\91964\Desktop\Klarix\super_resolution\sat_inputs_128"


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


print("=" * 55)
print("CREATING 128x128 INPUTS FOR TRUE 4X EVALUATION")
print("=" * 55)


count = 0


for filename in sorted(os.listdir(GT_FOLDER)):

    if not filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        continue

    # Only use the five Sentinel patches
    if not filename.lower().startswith("sentinel_patch_"):
        continue

    # Ignore anything that isn't the 512x512 GT patch
    if "_lr_" in filename.lower():
        continue

    image_path = os.path.join(GT_FOLDER, filename)

    image = cv2.imread(image_path)

    if image is None:
        print(f"Could not load: {filename}")
        continue

    height, width = image.shape[:2]

    if width != 512 or height != 512:
        print(
            f"Skipping {filename}: "
            f"expected 512x512, got {width}x{height}"
        )
        continue

    # True 4x degradation:
    # 512x512 -> 128x128
    lr = cv2.resize(
        image,
        (128, 128),
        interpolation=cv2.INTER_AREA
    )

    output_name = (
        os.path.splitext(filename)[0]
        + "_lr_128.png"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_name
    )

    cv2.imwrite(output_path, lr)

    print(
        f"{filename} -> "
        f"{output_name} "
        f"(512x512 -> 128x128)"
    )

    count += 1


print()
print(f"Created {count} input image(s).")
print("Output folder:")
print(OUTPUT_FOLDER)