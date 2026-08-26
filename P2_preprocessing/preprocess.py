from pathlib import Path
from PIL import Image


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
HR_DIR = BASE_DIR / "data" / "hr"
LR_DIR = BASE_DIR / "data" / "lr"

# Create output folders if they don't exist
HR_DIR.mkdir(parents=True, exist_ok=True)
LR_DIR.mkdir(parents=True, exist_ok=True)


def preprocess_image(image_path, output_name="sentinel_image"):
    """
    Converts a raw image to RGB, center-crops it,
    creates a 512x512 reference image and a 256x256 LR image.
    """

    # Load image
    img = Image.open(image_path)

    print(f"Original size: {img.size}")
    print(f"Original mode: {img.mode}")

    # Convert RGBA / other formats to RGB
    img = img.convert("RGB")

    # Center crop to square
    width, height = img.size
    side = min(width, height)

    left = (width - side) // 2
    top = (height - side) // 2
    right = left + side
    bottom = top + side

    img_square = img.crop((left, top, right, bottom))

    # Create standardized reference image
    img_hr = img_square.resize(
        (512, 512),
        Image.Resampling.LANCZOS
    )

    # Create simulated LR image
    img_lr = img_hr.resize(
        (256, 256),
        Image.Resampling.BICUBIC
    )

    # Output paths
    hr_path = HR_DIR / f"{output_name}_hr_512.png"
    lr_path = LR_DIR / f"{output_name}_lr_256.png"

    # Save images
    img_hr.save(hr_path)
    img_lr.save(lr_path)

    print("\nPreprocessing complete!")
    print(f"HR saved to: {hr_path}")
    print(f"LR saved to: {lr_path}")


if __name__ == "__main__":

    # Automatically find PNG images in raw folder
    images = list(RAW_DIR.glob("*.png"))

    if not images:
        print("No PNG images found in data/raw/")
    else:
        for image_path in images:
            print(f"\nProcessing: {image_path.name}")

            output_name = image_path.stem
            preprocess_image(image_path, output_name)