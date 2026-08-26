import cv2
from skimage.metrics import structural_similarity


def calculate_psnr(reference, reconstructed):
    """
    Calculate PSNR between a reference image
    and a reconstructed image.
    """

    if reference.shape != reconstructed.shape:
        raise ValueError(
            "Reference and reconstructed images "
            "must have the same dimensions."
        )

    psnr = cv2.PSNR(reference, reconstructed)

    return psnr

def calculate_ssim(reference, reconstructed):
    """
    Calculate SSIM between a reference image
    and a reconstructed image.
    """

    if reference.shape != reconstructed.shape:
        raise ValueError(
            "Reference and reconstructed images "
            "must have the same dimensions."
        )

    # Convert RGB/BGR images to grayscale
    reference_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    reconstructed_gray = cv2.cvtColor(
        reconstructed, cv2.COLOR_BGR2GRAY
    )

    ssim = structural_similarity(
        reference_gray,
        reconstructed_gray,
        data_range=255
    )

    return ssim

if __name__ == "__main__":

    reference = cv2.imread("test_reference.png")

    reconstructed = reference.copy()

    # Make a small modification
    reconstructed[0:20, 0:20] = 0

    psnr = calculate_psnr(
        reference,
        reconstructed
    )

    ssim = calculate_ssim(
        reference,
        reconstructed
    )

    print(f"PSNR: {psnr} dB")
    print(f"SSIM: {ssim}")