from pathlib import Path

from PIL import Image
import numpy as np

from inference import segment_satellite_image


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_IMAGE = BASE_DIR / "test-images" / "667.png"
OUTPUT_IMAGE = BASE_DIR / "test-images" / "667_segmentation.png"


# --------------------------------------------------
# LOVE DA CLASS COLORS
# --------------------------------------------------

CLASS_COLORS = {
    0: (0, 0, 0),          # Ignore
    1: (128, 128, 128),    # Background
    2: (255, 0, 0),        # Building
    3: (255, 255, 0),      # Road
    4: (0, 0, 255),        # Water
    5: (139, 69, 19),      # Barren
    6: (0, 128, 0),        # Forest
    7: (255, 165, 0),      # Agriculture
}


# --------------------------------------------------
# CREATE COLORED SEGMENTATION MAP
# --------------------------------------------------

def create_segmentation_visualization(
    predicted_mask,
    output_path
):

    height, width = predicted_mask.shape

    visualization = np.zeros(
        (height, width, 3),
        dtype=np.uint8
    )

    for class_id, color in CLASS_COLORS.items():

        visualization[predicted_mask == class_id] = color

    Image.fromarray(visualization).save(
        output_path
    )

    print("Segmentation visualization saved to:")
    print(output_path)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("P4 SEGMENTATION VISUALIZATION")
    print("=" * 60)

    print("Input image:", INPUT_IMAGE)

    # Run P4 inference
    mask = segment_satellite_image(
        str(INPUT_IMAGE)
    )

    # Create visualization
    create_segmentation_visualization(
        mask,
        OUTPUT_IMAGE
    )

    print("\nVisualization completed successfully!")