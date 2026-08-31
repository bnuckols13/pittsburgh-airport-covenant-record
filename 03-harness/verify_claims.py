#!/usr/bin/env python3
"""verify_claims.py — the machine gate for the ARTICLE-v15 fact check.

Two gates, in order. Either one failing exits non-zero.

  1. Hash gate.   Every vault document named in factcheck.json still hashes to the
                  SHA-256 recorded there.
  2. Anchor gate. Every anchor string recorded for a claim is still present on the
                  PDF page it cites, after whitespace and typographic normalisation.

An anchor is the literal run of text a claim rests on. If a document is re-captured
and a figure moves or changes, the anchor misses and the claim stops being citable.
This is the same discipline as verify_quotes.py, applied to claims rather than quotes.

Usage, from the investigation root:

    python 03-harness/verify_claims.py
    python 03-harness/verify_claims.py --ledger v2/factcheck-v15/factcheck.json
    python 03-harness/verify_claims.py --json          # machine-readable report
    python 03-harness/verify_claims.py --claim C-044   # one claim

Requires pdftotext (poppler-utils) on PATH. Text extractions are cached in
02-data/.pagecache/ and rebuilt when a PDF's hash changes.
"""
import argparse, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "v2", "factcheck-v16", "factcheck.json")
CACHE = os.path.join(ROOT, "02-data", ".pagecache")

DASHES = {"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
          "‘": "'", "’": "'", "“": '"', "”": '"', " ": " "}


def norm(s):
    for a, b in DASHES.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Two deterministic extractions. Financial tables in these Official Statements
# survive one mode or the other, never reliably both: -layout preserves the visual
# grid but splits a transposed table's label from its figures, while -raw keeps a
# printed row contiguous but loses column alignment. An anchor is satisfied if it
# appears in either page rendering, which is the gate's original matching unit
# (whole page, whitespace-normalised) applied once per mode rather than once total.
MODES = ("layout", "raw")


def pages(source_id, pdf_path, digest, mode="layout"):
    os.makedirs(CACHE, exist_ok=True)
    cached = os.path.join(CACHE, f"{source_id}.{digest[:16]}.{mode}.txt")
    if not os.path.exists(cached):
        for stale in os.listdir(CACHE):
            if stale.startswith(source_id + "."):
                os.remove(os.path.join(CACHE, stale))
        for m in MODES:
            out = os.path.join(CACHE, f"{source_id}.{digest[:16]}.{m}.txt")
            subprocess.run(["pdftotext", f"-{m}", pdf_path, out], check=True)
    with open(cached, encoding="utf-8", errors="replace") as f:
        return f.read().split("")


def anchor_hit(source_id, pdf_path, digest, pdf_page, want):
    """Return the extraction mode carrying `want` on `pdf_page`, or None."""
    needle = norm(want)
    for m in MODES:
        pg = pages(source_id, pdf_path, digest, m)
        if pdf_page - 1 >= len(pg):
            continue
        if needle in norm(pg[pdf_page - 1]):
            return m
    return None



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--claim")
    ap.add_argument("--ledger", default=LEDGER)
    a = ap.parse_args()

    doc = json.load(open(a.ledger, encoding="utf-8"))
    report = {"hash_gate": [], "anchor_gate": [], "ok": True}

    # gate 1
    text_cache = {}
    for sid, s in doc["sources"].items():
        if not s.get("sha256") or not s.get("vault_path" if "vault_path" in s else "path"):
            continue
        rel = s.get("path") or s.get("vault_path")
        p = os.path.normpath(os.path.join(ROOT, rel))
        if not os.path.exists(p):
            report["hash_gate"].append({"source_id": sid, "result": "MISSING", "path": rel})
            report["ok"] = False
            continue
        got = sha256(p)
        ok = got == s["sha256"]
        report["hash_gate"].append({"source_id": sid, "result": "OK" if ok else "MISMATCH",
                                    "expected": s["sha256"], "got": got})
        if not ok:
            report["ok"] = False
        else:
            text_cache[sid] = (p, got)

    # gate 2
    for c in doc["claims"]:
        if a.claim and c["claim_id"] != a.claim:
            continue
        for anc in c.get("anchors", []):
            sid = anc["source_id"]
            if sid not in text_cache:
                report["anchor_gate"].append({"claim_id": c["claim_id"], "source_id": sid,
                                              "result": "NO_DOC"})
                report["ok"] = False
                continue
            p, digest = text_cache[sid]
            for want in anc["must_contain"]:
                mode = anchor_hit(sid, p, digest, anc["pdf_page"], want)
                report["anchor_gate"].append({
                    "claim_id": c["claim_id"], "source_id": sid, "pdf_page": anc["pdf_page"],
                    "result": "OK" if mode else "MISS", "mode": mode, "text": want})
                if not mode:
                    report["ok"] = False

    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        hs = report["hash_gate"]
        print(f"hash gate   {sum(1 for r in hs if r['result']=='OK')}/{len(hs)} documents match")
        for r in hs:
            if r["result"] != "OK":
                print(f"  {r['result']}  {r['source_id']}")
        ag = report["anchor_gate"]
        print(f"anchor gate {sum(1 for r in ag if r['result']=='OK')}/{len(ag)} anchors present")
        for r in ag:
            if r["result"] != "OK":
                print(f"  {r['result']}  {r['claim_id']}  {r['source_id']} pdf {r.get('pdf_page','?')}"
                      f"  {r.get('text','')[:70]}")
        counts = doc["counts"]
        print()
        print(f"ledger: {counts.get('total')} claims  "
              f"{counts.get('failed',0)} fail  {counts.get('unsourced',0)} unsourced  "
              f"{counts.get('attention',0)} attention  "
              f"{counts.get('verified',0)+counts.get('verified_c',0)} verified  "
              f"{counts.get('slot',0)} slots")
        print("PASS" if report["ok"] else "FAIL")

    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
