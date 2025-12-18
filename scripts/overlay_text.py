import sys
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont


def find_font() -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=48)
    return ImageFont.load_default()


def overlay_text(
    src_path: Path,
    name: str,
    date_str: str,
    dst_path: Path | None = None,
) -> Path:
    img = Image.open(src_path).convert("RGBA")
    W, H = img.size

    # dynamic sizing
    base_font = find_font()
    # Scale font roughly with image height
    scale = max(32, int(H * 0.05))
    try:
        font = ImageFont.truetype(base_font.path, size=scale)  # type: ignore
    except Exception:
        font = base_font

    draw = ImageDraw.Draw(img, "RGBA")

    # Text content
    lines = [name, date_str]

    # Measure box
    padding_x = int(W * 0.02)
    padding_y = int(H * 0.015)
    line_heights = []
    max_w = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_w = max(max_w, w)
        line_heights.append(h)
    box_w = max_w + padding_x * 2
    box_h = sum(line_heights) + padding_y * (len(lines) + 1)

    # Bottom-left position
    x = padding_x
    y = H - box_h - padding_y

    # Background rectangle (semi-transparent black)
    rect_color = (0, 0, 0, 140)
    draw.rectangle([(x - padding_x, y - padding_y), (x - padding_x + box_w, y - padding_y + box_h)], fill=rect_color)

    # Text colors
    text_color = (255, 255, 255, 255)

    ty = y
    for i, line in enumerate(lines):
        draw.text((x, ty), line, font=font, fill=text_color)
        ty += line_heights[i] + padding_y

    if dst_path is None:
        dst_path = src_path

    # Save as JPEG, flatten alpha
    out_img = img.convert("RGB")
    out_img.save(dst_path, format="JPEG", quality=92)
    return dst_path


def main():
    if len(sys.argv) < 4:
        print("Usage: python scripts/overlay_text.py <image_path> <name> <date_text> [<output_path>]")
        sys.exit(1)

    src = Path(sys.argv[1])
    name = sys.argv[2]
    date_text = sys.argv[3]
    dst = Path(sys.argv[4]) if len(sys.argv) > 4 else None

    result = overlay_text(src, name, date_text, dst)
    print(f"Saved: {result}")


if __name__ == "__main__":
    main()
