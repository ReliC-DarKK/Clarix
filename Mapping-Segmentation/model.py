import torch
from pathlib import Path

from transformers import (
    SegformerImageProcessor,
    SegformerForSemanticSegmentation,
)

# CONFIGURATION
MODEL_NAME = "wu-pr-gw/segformer-b2-finetuned-with-LoveDA"

NUM_CLASSES = 8

# CORRECTED: was pointing at epoch_3, project is now on epoch_6.
CHECKPOINT_PATH = (
    Path(__file__).resolve().parent
    / "weights"
    / "segformer_loveda_epoch_6.pth"
)

# DEVICE
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# LOAD SEGFORMER PROCESSOR
processor = SegformerImageProcessor.from_pretrained(
    MODEL_NAME
)

# CREATE MODEL ARCHITECTURE
model = SegformerForSemanticSegmentation.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_CLASSES,
    ignore_mismatched_sizes=True
)

# LOAD FINE-TUNED CHECKPOINT
if not CHECKPOINT_PATH.exists():
    raise FileNotFoundError(
        f"Checkpoint not found: {CHECKPOINT_PATH}"
    )

checkpoint = torch.load(
    CHECKPOINT_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

# PREPARE MODEL FOR INFERENCE
model.to(DEVICE)
model.eval()

# CORRECTED: checkpoint dicts from different training runs don't always
# carry "epoch"/"loss" keys (e.g. a bare state_dict-only save). Use .get
# so importing this module never crashes on missing metadata - it just
# prints "unknown" instead.
_checkpoint_epoch = checkpoint.get("epoch", "unknown")
_checkpoint_loss = checkpoint.get("loss", "unknown")


def print_model_info():
    """Print a one-time summary of the loaded model. Kept as an
    explicit function (rather than running at import time) so that
    importing this module from inference.py or visualization.py
    doesn't print the banner on every import - only when this file is
    run directly, or when something explicitly wants to log it."""
    print("=" * 60)
    print("P4 SEGFORMER MODEL LOADED")
    print("=" * 60)
    print("Model:", MODEL_NAME)
    print("Device:", DEVICE)
    print("Checkpoint:", CHECKPOINT_PATH)
    print("Checkpoint epoch:", _checkpoint_epoch)
    print("Checkpoint loss:", _checkpoint_loss)
    print("Number of classes:", NUM_CLASSES)
    print("Model ready for inference.")


# CORRECTED: banner now only prints when model.py is run directly,
# not every time another module in the pipeline imports model/processor/DEVICE.
if __name__ == "__main__":
    print_model_info()
