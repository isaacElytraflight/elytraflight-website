"""Rebuild + check all batch2b banks: python3 gen/batch2b_build_all.py"""
import subprocess, sys, os
H = os.path.dirname(os.path.abspath(__file__))
for m in ["batch2b_a.py", "batch2b_b.py", "batch2b_c.py", "batch2b_d.py", "batch2b_e.py", "batch2b_validate.py", "batch2b_verify.py"]:
    r = subprocess.run([sys.executable, os.path.join(H, m)], capture_output=True, text=True)
    print(f"== {m}: exit {r.returncode}"); print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
    if r.returncode: sys.exit(r.returncode)
