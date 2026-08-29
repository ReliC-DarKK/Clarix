from pathlib import Path

import sys
from PIL import Image

# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# P1 Super Resolution directory
SR_DIR = BASE_DIR / "super_resolution"

# Make P1 module importable
if str(SR_DIR) not in sys.path:
    sys.path.insert(0, str(SR_DIR))

from sr_engine import load_sr_model, super_resolve


# --------------------------------------------------
# Load P1 model only once
# --------------------------------------------------

_model = None
_device = None


def get_sr_model():
    """
    Load the P1 super-resolution model once and reuse it.
    """
    global _model, _device

    if _model is None:
        weights_path = (
            SR_DIR
            / "weights"
            / "RealESRGAN_x4plus.pth"
        )

        print("Loading super-resolution model...")

        _model, _device = load_sr_model(
            str(weights_path)
        )

        print(
            f"Super-resolution model loaded on {_device}"
        )

    return _model, _device


# --------------------------------------------------
# Run P1 Super Resolution
# --------------------------------------------------

def run_super_resolution(
    input_path: str,
    output_path: str,
    model,
    device
):
    """
    Run P1 Real-ESRGAN super-resolution on an LR image.

    Input:
        256x256 LR image

    Output:
        1024x1024 SR image
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result = super_resolve(
        input_path=input_path,
        output_path=str(output_path),
        model=model,
        device=device,
        tile_size=256,
        tile_pad=10,
        scale=4
    )

    return result


# --------------------------------------------------
# P3 Bicubic Upscaling
# --------------------------------------------------

def run_bicubic(
    input_path: str,
    output_path: str
):
    """
    Run P3 Bicubic interpolation baseline.

    Input:
        256x256 LR image

    Output:
        1024x1024 Bicubic image
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Starting P3 bicubic upscaling...")

    # Open LR image
    image = Image.open(input_path).convert("RGB")

    print(
        f"Bicubic input size: {image.size}"
    )

    # 4x bicubic upscaling
    bicubic_image = image.resize(
        (1024, 1024),
        Image.Resampling.BICUBIC
    )

    # Save output
    bicubic_image.save(output_path)

    print(
        f"Bicubic output saved to: {output_path}"
    )

    return str(output_path)