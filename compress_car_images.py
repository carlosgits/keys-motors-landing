"""
Compress AI-generated car images for web delivery.

Originals are ~3MB each at 1536x1024. We need ~150-300KB at 1400x933
(close to the 16:11 native ratio) for fast page loads on mobile + Google Ads.

Run after generate_car_images.py.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

SRC_DIR = Path(__file__).resolve().parent / "assets" / "cars"
OUT_DIR = SRC_DIR  # overwrite in place

TARGET_WIDTH = 1400  # hero needs ~760-1000 max displayed, 1400 covers retina
QUALITY = 78         # good balance for outdoor photo content
PROGRESSIVE = True

def compress(path: Path):
    src_size = path.stat().st_size
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        ratio = TARGET_WIDTH / im.width
        new_h = int(im.height * ratio)
        resized = im.resize((TARGET_WIDTH, new_h), Image.LANCZOS)
        resized.save(
            path,
            format="JPEG",
            quality=QUALITY,
            optimize=True,
            progressive=PROGRESSIVE,
        )
    dst_size = path.stat().st_size
    pct = (1 - dst_size / src_size) * 100
    print(f"  [OK] {path.name}: {src_size:,} -> {dst_size:,} bytes (-{pct:.1f}%)")

def main():
    files = sorted(SRC_DIR.glob("*.jpg"))
    print(f"Compressing {len(files)} images in {SRC_DIR}")
    total_before = sum(p.stat().st_size for p in files)
    for p in files:
        compress(p)
    total_after = sum(p.stat().st_size for p in files)
    print()
    print(f"Total: {total_before:,} -> {total_after:,} bytes "
          f"(-{(1 - total_after/total_before)*100:.1f}%)")

if __name__ == "__main__":
    main()
