from pathlib import Path


def run_pipeline(
    input_path: Path,
    output_dir: Path,
):
    """
    Main Clarix processing pipeline.

    Current flow:

    Upload
       ↓
    Backend
       ↓
    Pipeline

    P2 preprocessing, P1 super-resolution,
    P3 evaluation and P4 mapping will be
    connected here.
    """

    return {
        "status": "uploaded",
        "input_path": str(input_path),
        "output_dir": str(output_dir),
    }