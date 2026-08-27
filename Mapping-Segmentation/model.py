import torch
from pathlib import Path

from transformers import (
    SegformerImageProcessor,
    SegformerForSemanticSegmentation,
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

MODEL_NAME = "wu-pr-gw/segformer-b2-finetuned-with-LoveDA"

NUM_CLASSES = 8

CHECKPOINT_PATH = (
    Path(__file__).resolve().parent
    / "weights"
    / "segformer_loveda_epoch_3.pth"
)


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# --------------------------------------------------
# LOAD SEGFORMER PROCESSOR
# --------------------------------------------------

processor = SegformerImageProcessor.from_pretrained(
    MODEL_NAME
)


# --------------------------------------------------
# CREATE MODEL ARCHITECTURE
# --------------------------------------------------

model = SegformerForSemanticSegmentation.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_CLASSES,
    ignore_mismatched_sizes=True
)


# --------------------------------------------------
# LOAD FINE-TUNED CHECKPOINT
# --------------------------------------------------

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


# --------------------------------------------------
# PREPARE MODEL FOR INFERENCE
# --------------------------------------------------

model.to(DEVICE)
model.eval()


# --------------------------------------------------
# MODEL INFORMATION
# --------------------------------------------------

print("=" * 60)
print("P4 SEGFORMER MODEL LOADED")
print("=" * 60)

print("Model:", MODEL_NAME)
print("Device:", DEVICE)
print("Checkpoint:", CHECKPOINT_PATH)
print("Checkpoint epoch:", checkpoint["epoch"])
print("Checkpoint loss:", checkpoint["loss"])
print("Number of classes:", NUM_CLASSES)
print("Model ready for inference.")