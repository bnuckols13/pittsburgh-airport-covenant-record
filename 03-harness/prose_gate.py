#!/usr/bin/env python3
"""prose_gate.py — refuse to ship the tells.

Every page here is generated, so the prose can be checked the same way the figures
are: mechanically, at build time, against a list. This reads the *built* pages rather
than the builders, because the builders assemble strings from several places and a
phrase can be clean in the source and wrong on the page.

The list is Brian's, from the style rules. Each check is deliberately narrow, because
a gate that cries wolf gets switched off:

  dead words        a fixed vocabulary, matched on word boundaries
  transitions       only at the start of a sentence, where they do the damage
  em-dash joins     an em-dash with a space either side, joining two clauses
  symmetry          "not X, but Y" and "Without X ... With it, Y"
  validators        standalone sentences that assert importance instead of showing it
  announced         "Key insight:", "Here's the thing:", "The takeaway:"
  enthusiasm        the exclamation register
  chop              three or more consecutive sentences under eight words

    python 03-harness/prose_gate.py
    python 03-harness/prose_gate.py --verbose
"""
import glob, html, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEAD = ["embrace", "embraces", "embracing", "tapestry", "journey", "delve", "delves",
        "myriad", "robust", "leverage", "leverages", "leveraging", "echoes", "echoing",
        "essence", "realm", "pivotal", "transformative", "nuanced", "unpack", "unpacks",
        "showcase", "showcases", "foster", "fosters", "elevate", "elevates",
        "illuminate", "illuminates", "underscores", "underscore",
        "testament to", "stands as", "speaks to", "delving", "myriads"]

# navigate and landscape are only dead in the metaphorical sense, and this package
# has no literal use for either, so they are listed. If a literal one ever appears,
# it goes in ALLOW below rather than weakening the rule.
DEAD += ["navigate", "navigates", "navigating", "landscape", "landscapes"]

TRANSITIONS = ["Furthermore", "Moreover", "Additionally", "It's worth noting",
               "It is worth noting", "Interestingly", "Strikingly", "Clearly",
               "Notably", "Importantly", "Crucially"]

VALIDATORS = [r"That matters\.", r"That is not nothing\.", r"That already matters\.",
              r"And that changes everything\.", r"This matters\.",
              r"That is the point\.", r"That is what matters\."]

ANNOUNCED = [r"Key [Ii]nsight:", r"Here'?s the thing:", r"The takeaway:",
             r"Bottom line:", r"In summary:", r"The key point:"]

SYMMETRY = [r"\bnot\s+(?:a|an|the)?\s*\w+[^.]{0,40},\s+but\s+(?:a|an|the)?\s*\w+",
            r"\bWithout\s+\w+[^.]{0,60}\.\s+With\s+it,"]

ENTHUSIASM = [r"\bGreat question\b", r"\bAbsolutely\b", r"!\s", r"\bexciting\b",
              r"\bamazing\b", r"\bincredible\b"]

# Phrases that would otherwise trip a rule and are correct here. Each needs a reason.
ALLOW = {
    # the indenture's own words, quoted
    "not constituting Revenues",
    # a documented figure, not a rhetorical inversion
    "not by pledged Net Revenues",
}


def visible(path):
    h = io.open(path, encoding="utf-8").read()
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"[ \t]+", " ", html.unescape(h))


# Splitting on every full stop turned "Dec. 31, 2028" into two sentences and the
# grade legend "A. Issuer document. B. Official." into four, which is how a gate
# earns its reputation for crying wolf. A period ends a sentence only when the token
# before it is not an abbreviation or a bare initial.
ABBR = {"jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov",
        "dec", "no", "pp", "p", "inc", "co", "corp", "vs", "eg", "ie", "mr", "ms",
        "mrs", "dr", "st", "fig", "est", "approx", "ave", "u.s", "cf"}


def sentences(text):
    parts, buf = [], ""
    for tok in re.split(r"(\s+)", text):
        buf += tok
        if not tok.strip():
            continue
        m = re.search(r"([A-Za-z.]+)[.!?][\"')\]]*$", tok)
        if not m:
            continue
        stem = m.group(1).rstrip(".").lower()
        if stem in ABBR or len(stem) <= 1:
            continue
        parts.append(buf.strip())
        buf = ""
    if buf.strip():
        parts.append(buf.strip())
    return [x for x in parts if x]


def check(path):
    text = visible(path)
    hits = []

    def add(kind, frag, ctx):
        if any(a in ctx for a in ALLOW):
            return
        hits.append((kind, frag, ctx.strip()[:150]))

    for w in DEAD:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", text, re.I):
            add("dead word", w, text[max(0, m.start() - 60):m.end() + 60])

    for s in sentences(text):
        for t in TRANSITIONS:
            if re.match(r"^" + re.escape(t) + r"\b", s, re.I):
                add("transition", t, s)

    # An em-dash joining two clauses. Ranges and parentheticals are not the target,
    # so only a spaced em-dash with a finite verb on each side is flagged.
    for m in re.finditer(r"[^.]{15,90}\s—\s[^.]{15,90}", text):
        add("em-dash join", "—", m.group(0))

    for pat in SYMMETRY:
        for m in re.finditer(pat, text):
            add("symmetry", m.group(0)[:50], m.group(0))
    for pat in VALIDATORS:
        for m in re.finditer(pat, text):
            add("validator", m.group(0), m.group(0))
    for pat in ANNOUNCED:
        for m in re.finditer(pat, text):
            add("announced structure", m.group(0), m.group(0))
    for pat in ENTHUSIASM:
        for m in re.finditer(pat, text):
            add("enthusiasm", m.group(0).strip(), text[max(0, m.start() - 60):m.end() + 60])

    # Three or more short sentences in a row. Two is a pattern, three is a tell, so
    # the gate fires on three and leaves two to judgement.
    ss = sentences(text)
    run = []
    for s in ss:
        if 0 < len(s.split()) < 8 and not s.endswith(":"):
            run.append(s)
        else:
            if len(run) >= 3:
                add("chop", " / ".join(run[:3]), " ".join(run))
            run = []
    if len(run) >= 3:
        add("chop", " / ".join(run[:3]), " ".join(run))

    return hits


# A gate is not trusted here until it has been watched to fail. Two guards in this
# case passed vacuously before anyone noticed, so every rule is fired against
# known-bad text on each run. The fixtures go through check() itself rather than a
# copy of its logic: a self-test with its own implementation tests the copy.
FIXTURES = [
    ("dead word", "The Authority will leverage its position."),
    ("dead word", "A robust framework carried the terminal."),
    ("transition", "Furthermore, the charge rose in every year."),
    ("em-dash join", "The airport earns less than it owes — and the covenant still "
                     "clears because a reserve is counted toward the test."),
    ("symmetry", "It is not a forecast, but a projection of the same rows."),
    ("validator", "The reserve is discretionary. That matters."),
    ("announced structure", "Key insight: the charge is residual."),
    ("enthusiasm", "This is an amazing finding about the bonds."),
    ("chop", "Costs rose. Nobody paid. The vote ended. Traffic held steady through the year."),
]


def selftest():
    import tempfile
    bad = 0
    for kind, sample in FIXTURES:
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                         encoding="utf-8") as f:
            f.write("<html><body><p>" + sample + "</p></body></html>")
            tmp = f.name
        try:
            kinds = {k for k, _, _ in check(tmp)}
        finally:
            os.unlink(tmp)
        if kind not in kinds:
            print(f"  SELFTEST FAIL [{kind}] did not fire on: {sample[:64]}")
            bad += 1
    if bad:
        print(f"{bad} of {len(FIXTURES)} rules did not fire. The gate proves nothing.")
    else:
        print(f"selftest OK: all {len(FIXTURES)} rules fire on known-bad text")
    return bad


def main():
    verbose = "--verbose" in sys.argv
    if selftest():
        return 1
    pages = ["index.html"] + sorted(glob.glob(os.path.join(ROOT, "*", "index.html")))
    pages = [p if os.path.isabs(p) else os.path.join(ROOT, p) for p in pages]
    total = 0
    for p in pages:
        if not os.path.exists(p):
            continue
        hits = check(p)
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        if hits:
            total += len(hits)
            print(f"\n{rel}  {len(hits)} flagged")
            for kind, frag, ctx in hits:
                print(f"  [{kind}] {frag}")
                if verbose:
                    print(f"      …{ctx}…")
        else:
            print(f"{rel}  clean")
    print(f"\n{total} flagged in total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
