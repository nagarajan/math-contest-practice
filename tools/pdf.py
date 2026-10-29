#!/usr/bin/env python3
"""PDF helper for building the question banks.

Usage (run with ../.venv/bin/python or the project venv):
  pdf.py info   <pdf>
  pdf.py text   <pdf> <page>                 # text blocks with bounding boxes (PDF points)
  pdf.py render <pdf> <page> [--dpi 110] [--grid] [--out PATH]
                                             # render a page to PNG (default /tmp/mcp_render/...);
                                             # --grid overlays a labeled coordinate grid (PDF points)
  pdf.py crop   <pdf> <page> <x0> <y0> <x1> <y1> <out.png> [--dpi 200]
                                             # crop a region (PDF points) to PNG

Pages are 0-based. Coordinates are PDF points with origin at top-left, as reported by `text`
and drawn by `render --grid`.
"""
import argparse
import os
import sys

import pymupdf


def cmd_info(a):
    d = pymupdf.open(a.pdf)
    print(f"{a.pdf}: {d.page_count} pages")
    for i, p in enumerate(d):
        r = p.rect
        print(f"  page {i}: {r.width:.0f}x{r.height:.0f} pt, {len(p.get_text())} chars, {len(p.get_images())} images")


def cmd_text(a):
    d = pymupdf.open(a.pdf)
    p = d[a.page]
    for b in p.get_text("blocks"):
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        kind = "IMG" if b[6] == 1 else "TXT"
        print(f"[{kind} {x0:6.1f},{y0:6.1f},{x1:6.1f},{y1:6.1f}] {txt.strip()}")
    for img in p.get_image_info():
        x0, y0, x1, y1 = img["bbox"]
        print(f"[IMAGE {x0:6.1f},{y0:6.1f},{x1:6.1f},{y1:6.1f}]")
    for dr in _drawing_clusters(p):
        x0, y0, x1, y1 = dr
        print(f"[VECTOR {x0:6.1f},{y0:6.1f},{x1:6.1f},{y1:6.1f}]")


def _drawing_clusters(page):
    rects = [pymupdf.Rect(dw["rect"]) for dw in page.get_drawings() if dw["rect"].width * dw["rect"].height > 4]
    clusters = []
    for r in rects:
        merged = False
        for i, c in enumerate(clusters):
            if (c + (-6, -6, 6, 6)).intersects(r):
                clusters[i] = c | r
                merged = True
                break
        if not merged:
            clusters.append(pymupdf.Rect(r))
    changed = True
    while changed:
        changed = False
        out = []
        for c in clusters:
            for i, o in enumerate(out):
                if (o + (-6, -6, 6, 6)).intersects(c):
                    out[i] = o | c
                    changed = True
                    break
            else:
                out.append(c)
        clusters = out
    return [tuple(c) for c in clusters if c.width > 15 and c.height > 15 and c.width < page.rect.width * 0.95]


def cmd_render(a):
    d = pymupdf.open(a.pdf)
    p = d[a.page]
    if a.grid:
        shape = p.new_shape()
        w, h = p.rect.width, p.rect.height
        step = 50
        for x in range(0, int(w) + 1, step):
            shape.draw_line((x, 0), (x, h))
        for y in range(0, int(h) + 1, step):
            shape.draw_line((0, y), (w, y))
        shape.finish(color=(1, 0, 0), width=0.3, stroke_opacity=0.5)
        shape.commit()
        for x in range(0, int(w) + 1, step):
            for y in range(0, int(h) + 1, 100):
                p.insert_text((x + 1, y + 7), f"{x},{y}", fontsize=5, color=(1, 0, 0))
    pix = p.get_pixmap(dpi=a.dpi)
    out = a.out or os.path.join(
        "/tmp/mcp_render",
        f"{os.path.splitext(os.path.basename(a.pdf))[0]}_p{a.page}{'_grid' if a.grid else ''}.png",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pix.save(out)
    print(out)


def cmd_crop(a):
    d = pymupdf.open(a.pdf)
    p = d[a.page]
    clip = pymupdf.Rect(a.x0, a.y0, a.x1, a.y1) & p.rect
    pix = p.get_pixmap(dpi=a.dpi, clip=clip)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    pix.save(a.out)
    print(f"{a.out} {pix.width}x{pix.height}px")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("info"); s.add_argument("pdf"); s.set_defaults(f=cmd_info)
    s = sp.add_parser("text"); s.add_argument("pdf"); s.add_argument("page", type=int); s.set_defaults(f=cmd_text)
    s = sp.add_parser("render"); s.add_argument("pdf"); s.add_argument("page", type=int)
    s.add_argument("--dpi", type=int, default=110); s.add_argument("--grid", action="store_true"); s.add_argument("--out")
    s.set_defaults(f=cmd_render)
    s = sp.add_parser("crop"); s.add_argument("pdf"); s.add_argument("page", type=int)
    for k in ("x0", "y0", "x1", "y1"):
        s.add_argument(k, type=float)
    s.add_argument("out"); s.add_argument("--dpi", type=int, default=200); s.set_defaults(f=cmd_crop)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    sys.exit(main())
