#!/usr/bin/env python3
"""Fotoğraf, Video ve Ses merkezinin özgün simge, açılış ve mağaza görselleri (Pillow).
Üçüncü taraf görsel kullanılmaz.  pip install pillow && python tool/generate_assets.py"""
import math
import os
from PIL import Image, ImageDraw

BG_TOP, BG_BOTTOM, ACCENT, LIGHT = (58, 31, 79), (20, 10, 34), (255, 138, 101), (255, 236, 224)


def gradient(w, h):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3)))
    return im


def glyph(d, cx, cy, s, color=ACCENT):
    """Diyafram halkası, ortasında oynat üçgeni ve sağda ses dalgaları: özgün, sade çizim."""
    w = max(2, int(s // 14))
    r = s * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    # Diyafram kanatları (6 kısa çizgi)
    for i in range(6):
        a = math.pi / 3 * i + math.pi / 6
        x1, y1 = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        x2, y2 = cx + math.cos(a + 0.9) * r, cy + math.sin(a + 0.9) * r
        d.line([(x1, y1), (x2, y2)], fill=color, width=max(2, w // 2))
    # Oynat üçgeni
    t = r * 0.42
    d.polygon([(cx - t * 0.6, cy - t), (cx - t * 0.6, cy + t), (cx + t, cy)], fill=LIGHT)
    # Ses dalgaları
    for k, rr in enumerate((r * 1.25, r * 1.5)):
        box = [cx - rr, cy - rr, cx + rr, cy + rr]
        d.arc(box, start=-35, end=35, fill=color if k == 0 else LIGHT, width=w)


def icon(size=1024):
    im = gradient(size, size)
    glyph(ImageDraw.Draw(im), size / 2 - size * 0.04, size / 2, size * 0.62)
    return im


def main():
    os.makedirs("assets/branding", exist_ok=True)
    os.makedirs("store", exist_ok=True)
    ic = icon()
    ic.save("assets/branding/icon.png")
    fg = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(fg), 490, 512, 400)
    fg.save("assets/branding/icon_foreground.png")
    sp = Image.new("RGBA", (768, 768), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(sp), 370, 384, 300)
    sp.save("assets/branding/splash.png")
    a12 = Image.new("RGBA", (1152, 1152), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(a12), 556, 576, 380)
    a12.save("assets/branding/splash_android12.png")
    ic.resize((512, 512)).save("store/icon_512.png")
    fe = gradient(1024, 500)
    glyph(ImageDraw.Draw(fe), 490, 250, 300)
    fe.save("store/feature_graphic.png")
    print("assets ok")


if __name__ == "__main__":
    main()
