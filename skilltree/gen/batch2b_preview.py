"""Render every figure in my banks (or given figures) into one HTML page for visual QA."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from batch2b_lib import *
if __name__ == "__main__":
    html = ['<html><body style="background:#fff;color:#222;font-family:sans-serif;display:flex;flex-wrap:wrap;gap:8px">']
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        figs = [("inv", fig_inverting()), ("noninv", fig_noninverting()), ("fol", fig_follower()), ("fb", fig_feedback_blocks())]
        for n, f in figs: html.append(f'<div style="border:1px solid #ccc;width:340px"><small>{n}</small>{f}</div>')
    else:
        sel = sys.argv[1:] or MINE
        for sid in sel:
            p = f"{BANK}/{sid}.json"
            if not os.path.exists(p): continue
            for q in json.load(open(p))["questions"]:
                if "figure" in q:
                    html.append(f'<div style="border:1px solid #ccc;width:360px"><small>{q["id"]}</small>{q["figure"]}</div>')
    html.append("</body></html>")
    open("/tmp/b2b_figs.html", "w").write("".join(html))
