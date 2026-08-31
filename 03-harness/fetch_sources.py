#!/usr/bin/env python3
"""fetch_sources.py — rebuild the document vault from the public record.

Downloads every source in 01-sources-archive/sources.json to
01-sources-archive/raw/ and checks each against its recorded SHA-256. A file whose
hash does not match is deleted rather than kept, because a source that does not
hash is not the source the claims were checked against.

    python 03-harness/fetch_sources.py
    python 03-harness/fetch_sources.py --only os-2025ab
"""
import argparse, hashlib, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "01-sources-archive", "sources.json")
RAW = os.path.join(ROOT, "01-sources-archive", "raw")
UA = {"User-Agent": "pit-terminal-financing-record/1.0 (evidence package verifier)"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args()

    doc = json.load(open(MAN, encoding="utf-8"))
    os.makedirs(RAW, exist_ok=True)
    ok = bad = skip = 0

    for sid, s in sorted(doc["sources"].items()):
        if a.only and sid != a.only:
            continue
        url, want, name = s.get("url"), s.get("sha256"), s.get("vault_filename")
        if not (url and want and name):
            print(f"SKIP    {sid}: no url or no hash recorded")
            skip += 1
            continue
        dest = os.path.join(RAW, name)
        if os.path.exists(dest) and sha256(dest) == want:
            print(f"HAVE    {sid}  {name}")
            ok += 1
            continue
        print(f"GET     {sid}  {url[:76]}")
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:
            print(f"  FAILED to download: {e}")
            bad += 1
            continue
        got = sha256(dest)
        if got == want:
            print(f"  OK    {got[:16]}...")
            ok += 1
        else:
            os.remove(dest)
            print(f"  HASH MISMATCH. expected {want[:16]}... got {got[:16]}... file discarded")
            bad += 1

    print(f"\n{ok} verified, {bad} failed, {skip} skipped")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
