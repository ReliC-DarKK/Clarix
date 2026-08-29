import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# P1 super-resolution module
SR_FOLDER = PROJECT_ROOT / "super_resolution"

# Allow Python to import P1's sr_engine.py
sys.path.insert(0, str(SR_FOLDER))
from pathlib import Path


from sr_engine import load_sr_model, super_resolve


INPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "super_resolution"
    / "sat_inputs_128"
)

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "super_resolution"
    / "sat_outputs_512"
)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model, device = load_sr_model(
    weights_path=str(
        Path(__file__).resolve().parent.parent
        / "super_resolution"
        / "weights"
        / "RealESRGAN_x4plus.pth"
    )
)

    valid_exts = {
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff"
    }

    files = sorted(
        f for f in INPUT_DIR.iterdir()
        if f.suffix.lower() in valid_exts
    )

    print("=" * 55)
    print("GENERATING TRUE 4X AI SUPER-RESOLUTION OUTPUTS")
    print("=" * 55)

    print(f"Input folder : {INPUT_DIR}")
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Images       : {len(files)}")
    print()

    for idx, img_file in enumerate(files, 1):

        output_file = (
            OUTPUT_DIR
            / f"{img_file.stem}_sr_512.png"
        )

        print(
            f"[{idx}/{len(files)}] "
            f"{img_file.name} -> "
            f"{output_file.name}"
        )

        super_resolve(
            str(img_file),
            str(output_file),
            model,
            device,
            scale=4
        )

    print()
    print("AI 4x batch processing complete.")


if __name__ == "__main__":
    main()