#!/usr/bin/env python3
"""Read AoPS wiki pages through the Wayback Machine (artofproblemsolving.com blocks scripts).

Usage (project venv):
  aops.py page "2015 AMC 8 Problems"        # page as text: LaTeX kept from the math images'
                                              # alt text, figures listed as [FIGURE k: <url>]
  aops.py page "2015 AMC 8 Answer Key"
  aops.py page "2015 AMC 8 Problems/Problem 2"   # the community solutions page for one problem
  aops.py fig <figure-url> <out.webp>         # download a figure listed by `page` as WebP

Pages are cached under sources/aops/. Asymptote figures also come with their [asy] source in the
listing, which helps when describing or checking a figure.
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "sources", "aops")
UA = {"User-Agent": "Mozilla/5.0 (math-contest-practice; personal study app)"}


def _get(url, tries=6):
    delay = 3
    for i in range(tries):
        time.sleep(1.5)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
            if data[:2] == b"\x1f\x8b":
                import gzip

                data = gzip.decompress(data)
            return data
        except Exception as ex:
            code = getattr(ex, "code", None)
            if code == 404:
                raise
            if i == tries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def _snapshot(page_url):
    q = urllib.parse.urlencode({"url": page_url, "output": "json", "filter": "statuscode:200", "fl": "timestamp,original"})
    rows = json.loads(_get(f"https://web.archive.org/cdx/search/cdx?{q}") or b"[]")
    if len(rows) < 2:
        return None
    return rows[-1]


def fetch_page(title):
    os.makedirs(CACHE, exist_ok=True)
    slug = title.replace(" ", "_")
    path = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "~", slug) + ".html")
    if os.path.exists(path):
        cached = open(path, encoding="utf-8", errors="replace").read()
        if "<html" in cached[:3000].lower() or "<!doctype" in cached[:200].lower():
            return cached
        os.remove(path)
    url = "https://artofproblemsolving.com/wiki/index.php/" + urllib.parse.quote(slug, safe="/")
    snap = _snapshot(url) or _snapshot(url.replace("https://", "http://"))
    if not snap:
        sys.exit(f"no Wayback snapshot of {url} (try the title with different spelling/case, or the browser)")
    ts, orig = snap
    body = _get(f"https://web.archive.org/web/{ts}id_/{orig}").decode("utf-8", "replace")
    open(path, "w", encoding="utf-8").write(body)
    return body


def to_text(s):
    m = re.search(r'<div[^>]+class="mw-parser-output"[^>]*>(.*)', s, re.S) or re.search(r'<div id="mw-content-text"[^>]*>(.*)', s, re.S)
    s = m.group(1) if m else s
    s = re.split(r'<div class="printfooter"|<div id="catlinks"|<!--\s*NewPP', s)[0]
    s = re.sub(r'<div id="toc".*?</div>\s*</div>', "", s, flags=re.S)
    s = re.sub(r'<table[^>]*class="[^"]*toc[^"]*".*?</table>', "", s, flags=re.S)
    figs = []

    def img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        cls = re.search(r'class="([^"]*)"', tag)
        src = src.group(1) if src else ""
        if src.startswith("//"):
            src = "https:" + src
        alt = html.unescape(alt.group(1)) if alt else ""
        if cls and cls.group(1) in ("latex", "latexcenter") and not alt.startswith("[asy]"):
            out = f" $${alt.strip('$')}$$ " if cls.group(1) == "latexcenter" and alt.startswith("$$") else f" {alt} "
            return out.replace("<", "\x00")
        figs.append(src)
        extra = f"\n    asy source: {alt}" if alt.startswith("[asy]") else (f" (alt: {alt})" if alt else "")
        return f"\n[FIGURE {len(figs)}: {src}]{extra}\n".replace("<", "\x00")

    s = re.sub(r'<img(?:[^>"]|"[^"]*")*>', img, s)
    s = re.sub(r'<h(\d)[^>]*>(.*?)</h\1>', lambda m: "\n\n" + "#" * int(m.group(1)) + " " + re.sub(r"<[^>]+>", "", m.group(2)) + "\n", s, flags=re.S)
    s = re.sub(r"<li[^>]*>", "\n- ", s)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", s)
    s = re.sub(r"</t[dh]>", " | ", s)
    s = re.sub(r"<pre[^>]*>(.*?)</pre>", lambda m: "\n```\n" + m.group(1) + "\n```\n", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\x00", "<")
    s = re.sub(r"\[edit\]", "", s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def fetch_fig(url, out):
    if url.startswith("//"):
        url = "https:" + url
    tmp = os.path.join(CACHE, "figs", re.sub(r"[^A-Za-z0-9_.-]", "_", url.split("://", 1)[-1]))
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    if not os.path.exists(tmp):
        data = _get(f"https://web.archive.org/web/2024im_/{url}")
        open(tmp, "wb").write(data)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import pdf

    class A:
        pass

    a = A()
    a.src, a.out, a.max_width, a.trim = tmp, out, 700, True
    pdf.cmd_img(a)


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "page":
        print(to_text(fetch_page(" ".join(sys.argv[2:]))))
    elif len(sys.argv) == 4 and sys.argv[1] == "fig":
        fetch_fig(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
