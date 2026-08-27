# Clarix

Clarix is a deep-learning based prototype for super-resolution mapping of medium-resolution satellite imagery.

The project aims to improve the spatial detail of satellite images and use the resulting Super-Resolved imagery for land-cover mapping. The prototype combines image preprocessing, AI-based super-resolution, bicubic interpolation as a baseline, quantitative evaluation, and semantic segmentation.



## Project Pipeline

The current prototype follows this workflow:
```markdown
+---------------------------+
|      Satellite Image      |
+-------------+-------------+
              |
              v
+---------------------------+
|     Data Preprocessing    |
+-------------+-------------+
              |
              v
+---------------------------+
|  Medium-Resolution Input  |
+-------------+-------------+
              |
              v
+---------------------------+
|    AI Super-Resolution    |
+-------------+-------------+
              |
              v
+---------------------------+
|       Super-Resolved      |
|           Image           |
+-------------+-------------+
              |
              v
+---------------------------+
|        PSNR / SSIM        |
|         Evaluation        |
+-------------+-------------+
              |
              v
+---------------------------+
|   Land-Cover Segmentation |
+-------------+-------------+
              |
              v
+---------------------------+
|   Super-Resolution Map    |
+---------------------------+
```
## Main Components

### 1. Dataset and Preprocessing

Satellite imagery is prepared before it is passed to the super-resolution model.

For the prototype, high-resolution reference images are down-sampled to create simulated lower-resolution inputs. The original images are retained as reference images for evaluation.

The preprocessing stage handles:

    - Image loading
    - Cropping
    - Resizing and down-sampling
    - Normalization
    - Creation of low-resolution and reference image pairs
    - Train, validation, and test data organization

The prototype uses [Sentinel-2 imagery](https://browser.dataspace.copernicus.eu/) and extracted image patches.


### 2. AI Super-Resolution

The super-resolution module takes a lower-resolution satellite image and generates an image with increased spatial detail.

The initial prototype uses a pre-trained super-resolution approach rather than training a large model from scratch.

The output of this stage is passed to the evaluation and mapping modules.



### 3. Bicubic Baseline

Bicubic interpolation is used as a traditional baseline.

The same low-resolution input is upscaled using bicubic interpolation and compared against the AI-generated result.

This provides a reference for determining whether the deep learning approach provides an improvement over conventional image resizing.


### 4. Evaluation

The reconstructed images are evaluated against the reference images.

The prototype uses:
    - PSNR (Peak Signal-to-Noise Ratio)
    - SSIM (Structural Similarity Index)

The evaluation compares both the bicubic result and the AI super-resolution result.

Example:

|       Method        | PSNR | SSIM |
|---------------------|------|------|
|      Bicubic        | -    | -    |
| AI Super-Resolution | -    | -    |

The values are filled using the results obtained from the actual test images.


### 5. Land-Cover Mapping

The mapping stage takes the super-resolved image and performs semantic segmentation using
[[SegFormer](https://huggingface.co/docs/transformers/model_doc/segformer).

The purpose is to identify different land-cover regions within the image rather than only
increasing its resolution.

The prototype uses a [SegFormer-B2 fine-tuned on LoveDA](https://huggingface.co/wu-pr-gw/segformer-b2-finetuned-with-LoveDA), with
[LoveDA](https://github.com/Junjue-Wang/LoveDA) providing the land-cover training data.

The segmentation output is represented as a land-cover map and can also be overlaid on
the super-resolved image.

Typical classes include:

    - Vegetation
    - Water
    - Built-up areas
    - Roads
    - Other / Bare land
  

### 6. Frontend and Integration

The individual modules are combined into a single prototype application.

The intended flow is:

    1. Upload satellite image
    2. Preprocess the image
    3. Generate the super-resolved image
    4. Generate the bicubic baseline
    5. Compare the results
    6. Calculate PSNR and SSIM where reference data is available
    7. Generate the land-cover map
    8. Display the outputs

## Repository Structure

```text
Clarix/
│
├── P1_super_resolution/
│   ├── p1_requirements.txt
│   ├── p1_super_resolution.py
│   ├── p1_run_demo.py
│   └── p1_outputs/
│       └── p1_sr_output.png
│
├── P2_preprocessing/
│   └── preprocess.py
│
├── P3_evaluation/
│   ├── bicubic.py
│   ├── evaluation.py
│   └── outputs/
│
├── P4_mapping/
│   ├── p4_requirements.txt
│   ├── p4_landcover.py
│   ├── p4_run_demo.py
│   └── p4_outputs/
│       ├── p4_landcover_mask.png
│       ├── p4_landcover_map.png
│       └── p4_landcover_overlay.png
│
├── P5_integration/
│   └── ...
│
├── data/
│   ├── raw/
│   ├── hr/
│   └── lr/
│
├── .gitignore
└── README.md
