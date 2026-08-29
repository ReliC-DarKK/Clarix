import os
import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms.functional as TF

class ResidualDenseBlock(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x

class RRDB(nn.Module):
    def __init__(self, nf, gc=32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(nf, gc)
        self.rdb2 = ResidualDenseBlock(nf, gc)
        self.rdb3 = ResidualDenseBlock(nf, gc)

    def forward(self, x):
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        return out * 0.2 + x

class RRDBNet(nn.Module):
    def __init__(self, num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32):
        super().__init__()
        self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(num_feat, num_grow_ch) for _ in range(num_block)])
        self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_last = nn.Conv2d(num_feat, num_out_ch, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        fea = self.conv_first(x)
        body_fea = self.conv_body(self.body(fea))
        fea = fea + body_fea
        fea = self.lrelu(self.conv_up1(nn.functional.interpolate(fea, scale_factor=2, mode='nearest')))
        fea = self.lrelu(self.conv_up2(nn.functional.interpolate(fea, scale_factor=2, mode='nearest')))
        out = self.conv_last(self.lrelu(self.conv_hr(fea)))
        return out

def load_sr_model(weights_path='weights/RealESRGAN_x4plus.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32).to(device)

    os.makedirs(os.path.dirname(weights_path), exist_ok=True)
    if not os.path.exists(weights_path):
        print("Downloading RealESRGAN_x4plus weights...")
        os.system(f"wget -q https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -O {weights_path}")

    loadnet = torch.load(weights_path, map_location=device)
    keyname = 'params_ema' if 'params_ema' in loadnet else ('params' if 'params' in loadnet else list(loadnet.keys())[0])
    model.load_state_dict(loadnet[keyname], strict=True)
    model.eval()
    return model, device

def super_resolve(input_path, output_path, model, device, tile_size=256, tile_pad=10, scale=4):
    img = Image.open(input_path).convert('RGB')
    width, height = img.size
    out_width, out_height = width * scale, height * scale
    output_img = Image.new('RGB', (out_width, out_height))

    stride = tile_size - (tile_pad * 2)

    for y in range(0, height, stride):
        for x in range(0, width, stride):
            x_min = max(0, x - tile_pad)
            y_min = max(0, y - tile_pad)
            x_max = min(width, x + tile_size + tile_pad)
            y_max = min(height, y + tile_size + tile_pad)

            tile = img.crop((x_min, y_min, x_max, y_max))
            tile_t = TF.to_tensor(tile).unsqueeze(0).to(device)

            with torch.no_grad():
                out_tile_t = model(tile_t).clamp(0, 1)

            out_tile = TF.to_pil_image(out_tile_t.squeeze(0).cpu())

            rx_min = (x - x_min) * scale
            ry_min = (y - y_min) * scale

            crop_box = (
                rx_min, 
                ry_min, 
                rx_min + (min(x + tile_size, width) - x) * scale, 
                ry_min + (min(y + tile_size, height) - y) * scale
            )
            
            cropped_out_tile = out_tile.crop(crop_box)
            output_img.paste(cropped_out_tile, (x * scale, y * scale))

    output_img.save(output_path)
    return output_path