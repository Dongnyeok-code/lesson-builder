"""교과서·지도서 추출 그림 모아보기 시트 만들기.
사용: python3 contact_sheet.py <images폴더> [출력폴더]
 - <images폴더> 아래 하위 폴더(tb, gd 등)마다 30장씩 번호(tb001…)를 붙인 JPG 시트를 만든다.
 - 시트를 보고 슬라이드에 넣을 그림을 고른다. tb007 → images/tb/image_007.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(sys.argv[1]); out = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "_sheets"
out.mkdir(parents=True, exist_ok=True)
W, H, COLS, PER = 230, 250, 6, 30
for sub in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")):
    files = sorted(sub.glob("image_*.png")) + sorted(sub.glob("image_*.jp*g"))
    for k in range(0, len(files), PER):
        chunk = files[k:k + PER]
        rows = (len(chunk) + COLS - 1) // COLS
        sheet = Image.new("RGB", (W * COLS, H * rows), "white")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            im = Image.open(f).convert("RGBA"); im.thumbnail((W - 8, H - 30))
            bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[3])
            x, y = (i % COLS) * W, (i // COLS) * H
            sheet.paste(bg, (x + 4, y + 24))
            num = f.stem.split("_")[-1][-3:]
            d.rectangle([x, y, x + 70, y + 20], fill=(200, 30, 30)); d.text((x + 4, y + 4), f"{sub.name}{num}", fill="white")
        p = out / f"{sub.name}_{k // PER}.jpg"; sheet.save(p, quality=85); print(p)
