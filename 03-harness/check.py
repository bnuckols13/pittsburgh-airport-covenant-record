#!/usr/bin/env python3
"""check.py — fetch the vault, then run the claim gate. One command."""
import os, subprocess, sys

H = os.path.dirname(os.path.abspath(__file__))
for step in ("fetch_sources.py", "verify_claims.py"):
    print(f"\n=== {step} ===")
    rc = subprocess.run([sys.executable, os.path.join(H, step)]).returncode
    if rc:
        sys.exit(rc)
print("\nall gates passed")
