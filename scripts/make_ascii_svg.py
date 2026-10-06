from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


CHARS = " .:-=+*#%@"


def make_ascii(source: Path, output: Path, width: int = 86) -> None:
    image = Image.open(source).convert("RGB")
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    height = round(width * 0.52)
    image = ImageOps.grayscale(image).resize((width, height))
    image = ImageEnhance.Contrast(image).enhance(1.7)

    rows = []
    for y in range(height):
        row = "".join(CHARS[image.getpixel((x, y)) * (len(CHARS) - 1) // 255] for x in range(width))
        rows.append(row.rstrip())

    line_height = 14
    svg_height = height * line_height + 32
    text_rows = []
    for index, row in enumerate(rows):
        escaped = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text_rows.append(
            f'<text x="16" y="{28 + index * line_height}" class="row" '
            f'style="animation-delay:{index * 0.035:.3f}s">{escaped}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width * 8 + 32}" height="{svg_height}" viewBox="0 0 {width * 8 + 32} {svg_height}">
<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>
<style>
.row {{ font: 12px/1 monospace; letter-spacing: 1px; fill: #69f0a0; opacity: 0; animation: reveal .45s ease-out forwards; }}
@keyframes reveal {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: translateX(0); }} }}
@media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; opacity: 1; }} }}
</style>
{''.join(text_rows)}
</svg>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python scripts/make_ascii_svg.py SOURCE OUTPUT")
    make_ascii(Path(sys.argv[1]), Path(sys.argv[2]))
