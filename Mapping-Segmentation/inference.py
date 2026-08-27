from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F

from model import model, processor, DEVICE


def segment_satellite_image(image_path):
    
    #Load Image
    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)

    print("Input image shape:", image_array.shape)

    # Preprocess
    inputs = processor(
        images=image_array,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    # Run SegFormer
    with torch.no_grad():

        outputs = model(**inputs)

        logits = F.interpolate(
            outputs.logits,
            size=image_array.shape[:2],
            mode="bilinear",
            align_corners=False
        )

        predicted_mask = torch.argmax(
            logits,
            dim=1
        ).squeeze(0)

    # Move prediction to CPU
    predicted_mask = predicted_mask.cpu().numpy()
    predicted_mask = predicted_mask.astype(np.int64)

    print("Output mask shape:", predicted_mask.shape)

    print(
        "Predicted classes:",
        np.unique(predicted_mask).tolist()
    )

    return predicted_mask

# TEST
if __name__ == "__main__":

    test_image = "Mapping-Segmentation/test-images/667.png"

    mask = segment_satellite_image(test_image)

    print("\nP4 inference test successful!")
    print("Final mask shape:", mask.shape)

    print(
        "Final predicted classes:",
        np.unique(mask).tolist()
    )