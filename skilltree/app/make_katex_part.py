"""Builds parts/p1k_katex.html: KaTeX CSS (fonts inlined as base64 woff2) + katex.min.js, fully offline."""
import base64, os, re
H = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(H, "tests/node_modules/katex/dist")
css = open(os.path.join(K, "katex.min.css")).read()
def font(m):
    name = m.group(1)
    b = base64.b64encode(open(os.path.join(K, "fonts", name + ".woff2"), "rb").read()).decode()
    return f'src:url(data:font/woff2;base64,{b}) format("woff2")'
css2, n = re.subn(r'src:url\(fonts/([A-Za-z0-9_-]+)\.woff2\) format\("woff2"\)(?:,url\([^)]*\) format\("[a-z]+"\))*', font, css)
assert n >= 19 and "fonts/" not in css2, n
js = open(os.path.join(K, "katex.min.js")).read()
assert "</script" not in js
ver = re.search(r'version:"([0-9.]+)"', js)
out = (f'<!-- KaTeX {ver.group(1) if ver else ""} (MIT license, https://katex.org) inlined for offline math rendering -->\n'
       f'<style id="katexcss">{css2}</style>\n<script id="katexjs">{js}</script>\n')
open(os.path.join(H, "parts/p1k_katex.html"), "w").write(out)
print("fonts inlined:", n, "bytes:", len(out))
