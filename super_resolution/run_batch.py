from pathlib import Path
from sr_engine import load_sr_model, super_resolve

def process_batch(input_dir='sat_inputs', output_dir='sat_outputs'):
    model, device = load_sr_model()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    valid_exts = {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}
    files = [f for f in input_path.iterdir() if f.suffix.lower() in valid_exts]
    
    print(f"Processing {len(files)} patch(es) from {input_dir}...")
    for idx, img_file in enumerate(files, 1):
        out_file = output_path / f"{img_file.stem}_sr_1024{img_file.suffix}"
        print(f"[{idx}/{len(files)}] Super-resolving {img_file.name} -> {out_file.name}")
        super_resolve(str(img_file), str(out_file), model, device)
        
    print("Batch processing complete.")

if __name__ == "__main__":
    process_batch()