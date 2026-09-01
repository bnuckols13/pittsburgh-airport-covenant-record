#!/usr/bin/env python3
"""check.py — fetch the vault, re-render every generated page, run the claim gate.

--check re-renders a page in memory and byte-diffs it against the committed file, so a
page that has drifted from the data it claims to be built from fails here.
"""
import os, subprocess, sys

H = os.path.dirname(os.path.abspath(__file__))
STEPS = [("fetch_sources.py", []),
         ("build_front.py", ["--check"]),
         ("build_tools.py", ["--check"]),
         ("build_claims.py", ["--check"]),
         ("build_press.py", ["--check"]),
         ("prose_gate.py", []),
         ("verify_claims.py", [])]
for step, args in STEPS:
    print(f"\n=== {step} ===")
    rc = subprocess.run([sys.executable, os.path.join(H, step)] + args).returncode
    if rc:
        sys.exit(rc)
print("\nall gates passed")
