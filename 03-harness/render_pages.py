#!/usr/bin/env python3
"""Page-rendering harness for the Pittsburgh airport covenant record.

Run:    python3 -I 03-harness/render_pages.py
Check:  python3 -I 03-harness/render_pages.py --check

Reads 02-data/cited-pages.csv and the key_pages of 02-data/documents.csv,
resolves each doc to a PDF through the case's sources-v29.json registry
(sha256 verified before a PDF is opened), renders every cited page at 150 dpi
with a 40 dpi thumbnail, and locates the cited figures on the page.

Outputs (and nothing else):
  documents/pages/<doc>-p<NNN>.jpg
  documents/pages/thumb/<doc>-p<NNN>.jpg
  02-data/page-highlights.json
  02-data/page-manifest.csv

Rendering is deterministic: fixed dpi, fixed Pillow JPEG settings, no
timestamps or metadata.  --check re-renders in memory and compares the
sha256 of the JPEG bytes with what is on disk.
"""
import csv
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import fitz  # PyMuPDF
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
CASE = r"C:\Users\brian\journalism-master\investigations\pit-terminal-financing"
REGISTRY = os.path.join(CASE, "v2", "factcheck-v29", "sources-v29.json")

CITED = os.path.join(PKG, "02-data", "cited-pages.csv")
DOCS = os.path.join(PKG, "02-data", "documents.csv")
OUT_JSON = os.path.join(PKG, "02-data", "page-highlights.json")
OUT_CSV = os.path.join(PKG, "02-data", "page-manifest.csv")
PAGES_DIR = os.path.join(PKG, "documents", "pages")
THUMB_DIR = os.path.join(PAGES_DIR, "thumb")

DPI = 150
THUMB_DPI = 40
JPEG_QUALITY = 82
MAX_RECTS = 12
COMMON_TOKEN_MATCHES = 6  # more than this on one page: not a figure


def ascii_safe(s):
    return s.encode("ascii", "replace").decode("ascii")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- inputs
def split_pipe(s):
    return [x.strip() for x in (s or "").split("|") if x.strip()]


def load_page_list():
    """Return (ordered list of [doc, page, terms, claims], dropped strays)."""
    with open(DOCS, encoding="utf-8", newline="") as f:
        doc_rows = list(csv.DictReader(f))
    doc_ids = {r["id"] for r in doc_rows}

    pages = {}
    dropped = []
    with open(CITED, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["doc_id"] not in doc_ids:
                dropped.append((r["doc_id"], r["pdf_page"]))
                continue
            key = (r["doc_id"], int(r["pdf_page"]))
            ent = pages.setdefault(key, {"terms": [], "claims": []})
            for t in split_pipe(r["terms"]):
                if t not in ent["terms"]:
                    ent["terms"].append(t)
            for c in split_pipe(r["claim_ids"]):
                if c not in ent["claims"]:
                    ent["claims"].append(c)

    for r in doc_rows:
        kp = (r.get("key_pages") or "").strip()
        if not kp:
            continue
        for chunk in kp.split(";"):
            chunk = chunk.strip()
            if not chunk:
                continue
            n = chunk.split("|", 1)[0].strip()
            if not n.isdigit():
                continue
            pages.setdefault((r["id"], int(n)), {"terms": [], "claims": []})

    ordered = sorted(pages.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    return ordered, dropped


def load_registry():
    with open(REGISTRY, encoding="utf-8") as f:
        d = json.load(f)
    reg = {}
    for s in d["sources"]:
        rel = s.get("file") or s.get("path")
        reg[s["id"]] = {"rel": rel, "sha256": s["sha256"]}
    return reg


# ---------------------------------------------------------------- render
def pix_to_jpeg(pix, quality=JPEG_QUALITY):
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=False,
             progressive=False, subsampling=2)
    return buf.getvalue()


def render_page(page, dpi):
    pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
    return pix_to_jpeg(pix), pix.width, pix.height


def term_variants(term):
    t = term.strip().rstrip(",;.")
    out = []
    for v in (t, t.replace("$", ""), t.replace(",", ""),
              t.replace("$", "").replace(",", "")):
        v = v.strip()
        if v and v not in out:
            out.append(v)
    return out


def dedupe(rects):
    keep = []
    for r in sorted(rects, key=lambda r: (round(r.y0, 1), round(r.x0, 1))):
        if any(k.contains(r) or r.contains(k) for k in keep):
            # keep the larger of the two
            for i, k in enumerate(keep):
                if k.contains(r):
                    break
                if r.contains(k):
                    keep[i] = r
                    break
            continue
        keep.append(r)
    return keep


def find_term(page, term):
    """First variant (as given, $ stripped, comma removed, both) with a hit."""
    for v in term_variants(term):
        hits = dedupe([fitz.Rect(q) for q in page.search_for(v)])
        if hits:
            return hits
    return []


def frac(rect, page):
    """search_for rects are in unrotated page space; the rendered image is
    in displayed (rotated) space, so map through the rotation matrix."""
    page_rect = page.rect
    rect = fitz.Rect(rect) * page.rotation_matrix
    rect.normalize()
    w, h = page_rect.width, page_rect.height
    return [round(max(0.0, min(1.0, (rect.x0 - page_rect.x0) / w)), 4),
            round(max(0.0, min(1.0, (rect.y0 - page_rect.y0) / h)), 4),
            round(max(0.0, min(1.0, (rect.x1 - page_rect.x0) / w)), 4),
            round(max(0.0, min(1.0, (rect.y1 - page_rect.y0) / h)), 4)]


def locate_terms(page, terms):
    found = {}      # term -> [rect fractions]
    missing = []
    common = {}     # term -> match count (dropped)
    for t in terms:
        hits = find_term(page, t)
        if not hits:
            missing.append(t)
        elif len(hits) > COMMON_TOKEN_MATCHES:
            common[t] = len(hits)
        else:
            found[t] = [frac(r, page) for r in hits]
    # cap total rects at MAX_RECTS, round-robin so every term keeps a mark
    total = sum(len(v) for v in found.values())
    capped = 0
    unplotted = []
    if total > MAX_RECTS:
        keep = {t: [] for t in found}
        n = 0
        depth = 0
        while n < MAX_RECTS:
            progressed = False
            for t in found:
                if depth < len(found[t]) and n < MAX_RECTS:
                    keep[t].append(found[t][depth])
                    n += 1
                    progressed = True
            if not progressed:
                break
            depth += 1
        capped = total - n
        unplotted = [t for t, v in keep.items() if not v]
        found = {t: v for t, v in keep.items() if v}
    return found, missing, common, capped, unplotted


def build_record(doc, pdf_page, ent, page, doc_sha):
    jpg, w, h = render_page(page, DPI)
    thumb, _, _ = render_page(page, THUMB_DPI)
    name = "%s-p%03d.jpg" % (doc, pdf_page)
    found, missing, common, capped, unplotted = locate_terms(page, ent["terms"])
    rec = {
        "doc_id": doc,
        "pdf_page": pdf_page,
        "printed_page": page.get_label() or "",
        "image": "documents/pages/" + name,
        "thumb": "documents/pages/thumb/" + name,
        "width_px": w,
        "height_px": h,
        "sha256": doc_sha,
        "terms_found": found,
        "terms_missing": missing,
        "terms_common_dropped": common,
        "terms_found_unplotted": unplotted,
        "rects_capped": capped,
        "claim_ids": ent["claims"],
    }
    return rec, jpg, thumb


# ---------------------------------------------------------------- main
def open_pdfs(ordered, reg):
    """Verify sha256 for every PDF needed.  Returns (docs, skipped)."""
    docs = {}
    skipped = []
    for doc in sorted({k[0] for k, _ in ordered}):
        entry = reg.get(doc)
        if entry is None:
            skipped.append((doc, "not in sources-v29.json registry"))
            continue
        rel = entry["rel"]
        ext = os.path.splitext(rel)[1].lower()
        if ext != ".pdf":
            skipped.append((doc, "source is %s, not a PDF" % ext.lstrip(".")))
            continue
        path = os.path.join(CASE, rel.replace("/", os.sep))
        if not os.path.exists(path):
            skipped.append((doc, "registered file missing on disk"))
            continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            print("SHA MISMATCH for %s: registry %s, disk %s (%s)"
                  % (doc, entry["sha256"], actual, ascii_safe(rel)))
            print("Stopping. Nothing rendered.")
            sys.exit(2)
        docs[doc] = (path, actual)
    return docs, skipped


def main():
    check = "--check" in sys.argv[1:]
    ordered, dropped = load_page_list()
    reg = load_registry()
    docs, skipped = open_pdfs(ordered, reg)
    skipped_ids = {d for d, _ in skipped}

    records = []
    manifest = []
    oob = []
    drift = []
    files_expected = []
    handles = {}
    try:
        for (doc, pg), ent in ordered:
            if doc in skipped_ids:
                continue
            path, doc_sha = docs[doc]
            if doc not in handles:
                handles[doc] = fitz.open(path)
            pdf = handles[doc]
            if pg < 1 or pg > pdf.page_count:
                oob.append((doc, pg, pdf.page_count))
                continue
            page = pdf[pg - 1]
            rec, jpg, thumb = build_record(doc, pg, ent, page, doc_sha)
            records.append(rec)
            manifest.append([doc, pg, rec["image"], rec["thumb"],
                             len(rec["terms_found"]),
                             len(rec["terms_missing"]),
                             len(rec["terms_common_dropped"]),
                             len(rec["terms_found_unplotted"]), ""])
            ipath = os.path.join(PKG, rec["image"].replace("/", os.sep))
            tpath = os.path.join(PKG, rec["thumb"].replace("/", os.sep))
            files_expected.append((ipath, jpg))
            files_expected.append((tpath, thumb))
    finally:
        for h in handles.values():
            h.close()

    if check:
        for p, data in files_expected:
            if not os.path.exists(p):
                drift.append((p, "missing"))
            elif sha256_bytes(open(p, "rb").read()) != sha256_bytes(data):
                drift.append((p, "pixel hash differs"))
        # the highlight file must also match a fresh computation
        try:
            on_disk = json.load(open(OUT_JSON, encoding="utf-8"))
            if on_disk != json.loads(json.dumps(records)):
                drift.append((OUT_JSON, "content differs"))
        except Exception as e:
            drift.append((OUT_JSON, "unreadable: %s" % e))
        print("checked %d images (%d pages); pdf sha256 verified for %d docs"
              % (len(files_expected), len(records), len(docs)))
        if oob:
            print("out-of-range pages: %s" % oob)
        if drift:
            for p, why in drift:
                print("DRIFT: %s (%s)" % (ascii_safe(os.path.relpath(p, PKG)), why))
            print("check FAILED: %d drifted" % len(drift))
            sys.exit(1)
        print("check OK: no drift")
        sys.exit(0)

    os.makedirs(THUMB_DIR, exist_ok=True)
    for p, data in files_expected:
        with open(p, "wb") as f:
            f.write(data)

    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(records, f, indent=1, ensure_ascii=True)
        f.write("\n")

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["doc_id", "pdf_page", "image", "thumb", "n_terms_found",
                    "n_terms_missing", "n_terms_common_dropped",
                    "n_terms_found_unplotted", "note"])
        w.writerows(manifest)
        for doc, why in skipped:
            w.writerow([doc, "", "", "", "", "", "", "", "SKIPPED: " + why])
        for doc, pg, n in oob:
            w.writerow([doc, pg, "", "", "", "", "", "",
                        "SKIPPED: page out of range (PDF has %d pages)" % n])
        for doc, pg in dropped:
            w.writerow([doc, pg, "", "", "", "", "", "",
                        "DROPPED: doc_id not in documents.csv (regex stray)"])

    nf = sum(len(r["terms_found"]) for r in records)
    nm = sum(len(r["terms_missing"]) for r in records)
    nc = sum(len(r["terms_common_dropped"]) for r in records)
    nu = sum(len(r["terms_found_unplotted"]) for r in records)
    size = 0
    for p, data in files_expected:
        size += len(data)
    print("pages rendered: %d" % len(records))
    print("terms found (plotted): %d, found but unplotted (12-rect cap): %d, missing: %d, dropped as common tokens: %d" % (nf, nu, nm, nc))
    print("skipped ids: %s" % [(d, w) for d, w in skipped])
    print("out-of-range: %s" % oob)
    print("dropped stray rows: %s" % dropped)
    print("image bytes written: %d (%.1f MB)" % (size, size / 1048576.0))


if __name__ == "__main__":
    main()
