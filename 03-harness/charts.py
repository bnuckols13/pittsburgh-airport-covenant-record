#!/usr/bin/env python3
"""charts.py — parametric SVG primitives.

SOP-104: "build.py reads the CSV and emits SVG, nobody types a coordinate."
Every function here takes a Frame and a Scale and rows. None takes a literal
x or y from a caller. The only literals a plate spec may name are the frame
box and its margins.

Two disciplines are enforced here rather than documented and hoped for:

  assert_in_domain   a value that would render outside the plotting box stops
                     the build instead of being clipped silently.
  assert_single_basis a set of rows handed to one line may carry only one
                     basis. The Authority's residual calculation and FAA Form
                     5100-127 are two series and are never joined by a stroke.
  gapped_path        a missing year is a break in the line, never a segment
                     drawn through it.
"""
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence
import html as _html

# House tokens, from the tufte-viz reference. Charts never hard-code a hex;
# they name a variable so both themes and the print stylesheet follow.
C = {
    "ink": "var(--ink)", "ink2": "var(--ink2)", "muted": "var(--muted)",
    "grid": "var(--grid)", "axis": "var(--axis)", "blue": "var(--blue)",
    "blue_lt": "var(--blue-lt)", "aqua": "var(--aqua)", "yellow": "var(--yellow)",
    "orange": "var(--orange)", "red": "var(--red)", "surface": "var(--surface)",
}


def esc(s) -> str:
    return _html.escape(str(s), quote=True)


# --------------------------------------------------------------------------- geometry

@dataclass(frozen=True)
class Frame:
    w: float
    h: float
    l: float = 56
    r: float = 24
    t: float = 30
    b: float = 52

    @property
    def x0(self) -> float: return self.l

    @property
    def x1(self) -> float: return self.w - self.r

    @property
    def ytop(self) -> float: return self.t

    @property
    def ybot(self) -> float: return self.h - self.b

    def inset(self, x: float, y: float, w: float, h: float) -> "Frame":
        """A sub-frame in the same coordinate space, for small multiples."""
        return Frame(w=x + w, h=y + h, l=x, r=self.w - (x + w) if False else 0,
                     t=y, b=0)


class Scale:
    """Linear domain to pixel range. No magic numbers anywhere else."""

    def __init__(self, d0: float, d1: float, r0: float, r1: float):
        if d1 == d0:
            raise SystemExit("Scale: empty domain")
        self.d0, self.d1, self.r0, self.r1 = float(d0), float(d1), float(r0), float(r1)

    def __call__(self, v: float) -> float:
        return self.r0 + (float(v) - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)

    def clamped(self, v: float) -> bool:
        lo, hi = min(self.d0, self.d1), max(self.d0, self.d1)
        return not (lo <= float(v) <= hi)


class Band:
    """Evenly spaced categorical positions."""

    def __init__(self, labels: Sequence[str], r0: float, r1: float, pad: float = 0.5):
        self.labels = list(labels)
        n = len(self.labels)
        if n == 0:
            raise SystemExit("Band: no categories")
        self.step = (r1 - r0) / (n - 1 + 2 * pad)
        self._pos = {lab: r0 + self.step * (pad + i) for i, lab in enumerate(self.labels)}

    def center(self, label: str) -> float:
        if label not in self._pos:
            raise SystemExit(f"Band: no position for {label!r}")
        return self._pos[label]


def domain(values: Iterable[float], pad: float = 0.06,
           include: Iterable[float] = ()) -> tuple[float, float]:
    vals = [float(v) for v in values if v not in ("", None)] + [float(v) for v in include]
    if not vals:
        raise SystemExit("domain: no values")
    lo, hi = min(vals), max(vals)
    if lo == hi:
        lo, hi = lo - 1, hi + 1
    span = hi - lo
    return lo - span * pad, hi + span * pad


def nice_ticks(d0: float, d1: float, target: int = 5) -> list[float]:
    span = abs(d1 - d0)
    raw = span / max(target, 1)
    mag = 10 ** (len(str(int(raw))) - 1) if raw >= 1 else 0.01
    for m in (1, 2, 2.5, 5, 10):
        step = mag * m
        if span / step <= target + 1:
            break
    lo = (int(min(d0, d1) / step) + 1) * step
    out, v = [], lo
    while v <= max(d0, d1):
        out.append(round(v, 6))
        v += step
    return out


def assert_in_domain(sc: Scale, values: Iterable[float], where: str) -> None:
    bad = [v for v in values if v not in ("", None) and sc.clamped(v)]
    if bad:
        raise SystemExit(
            f"{where}: {bad!r} falls outside the scale domain "
            f"[{sc.d0:g}, {sc.d1:g}] and would be drawn off the canvas. "
            "Widen the domain from the data rather than clipping.")


# --------------------------------------------------------------------------- discipline

def assert_single_basis(rows: Sequence[dict], key: str = "basis", where: str = "") -> None:
    seen = {(r.get(key) or "").strip() for r in rows}
    seen.discard("")
    if len(seen) > 1:
        raise SystemExit(
            f"{where}: one line would join {sorted(seen)}. The Authority's residual "
            "calculation and FAA Form 5100-127 are two series and are never joined "
            "by a stroke. Split them into separate paths.")


def assert_plottable(rows: Sequence[dict], where: str, tier_key: str = "tier") -> None:
    """A clip may be an utterance. It may never be a figure."""
    bad = [(r.get("label") or r.get("year") or "?", r.get(tier_key))
           for r in rows if (r.get(tier_key) or "A").strip() != "A"]
    if bad:
        raise SystemExit(
            f"{where}: {bad!r} would be drawn as data and are not tier A. "
            "A clip may be an utterance and never a figure. Draw it as an "
            "annotation mark instead, or capture the document.")


# --------------------------------------------------------------------------- marks

def mark(grade: str, colour: str, x: float, y: float, r: float = 4.2) -> str:
    """Admiralty reliability, encoded in shape so it survives without colour.

    A solid disc, B disc with a cut-out core, C open ring, D and below dashed ring.
    """
    g = (grade or "F")[0].upper()
    if g == "A":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colour}"/>'
    if g == "B":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colour}"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.42:.1f}" fill="{C["surface"]}"/>')
    if g == "C":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" '
                f'stroke="{colour}" stroke-width="1.6"/>')
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{colour}" '
            f'stroke-width="1.6" stroke-dasharray="2.4 2"/>')


def grade_key(x: float, y: float, colour: str) -> str:
    """The legend is drawn by the same function that draws the data."""
    out, dx = [], 0.0
    for g, txt in (("A", "issuer document, hashed"), ("B", "official, not captured"),
                   ("C", "secondary or clip"), ("D", "interested party")):
        out.append(mark(g, colour, x + dx, y))
        out.append(f'<text class="ax" x="{x+dx+9:.1f}" y="{y+3.5:.1f}">{esc(txt)}</text>')
        dx += 150
    return "".join(out)


# --------------------------------------------------------------------------- axes

def axis_y(f: Frame, sc: Scale, ticks: Sequence[float],
           fmt: Callable[[float], str] = lambda v: f"{v:g}", labels: bool = True) -> str:
    out = []
    for t in ticks:
        y = sc(t)
        out.append(f'<line x1="{f.x0}" y1="{y:.1f}" x2="{f.x1}" y2="{y:.1f}" stroke="{C["grid"]}"/>')
        if labels:
            out.append(f'<text class="ax" x="{f.x0-7}" y="{y+4:.1f}" text-anchor="end">'
                       f'{esc(fmt(t))}</text>')
    return "".join(out)


def axis_x_years(f: Frame, sc: Scale, years: Sequence[int]) -> str:
    out = [f'<line x1="{f.x0}" y1="{f.ybot:.1f}" x2="{f.x1}" y2="{f.ybot:.1f}" stroke="{C["axis"]}"/>']
    for yr in years:
        out.append(f'<text class="ax" x="{sc(yr):.1f}" y="{f.ybot+18:.1f}" '
                   f'text-anchor="middle">{yr}</text>')
    return "".join(out)


def axis_x_band(f: Frame, b: Band, rotate: bool = False) -> str:
    out = [f'<line x1="{f.x0}" y1="{f.ybot:.1f}" x2="{f.x1}" y2="{f.ybot:.1f}" stroke="{C["axis"]}"/>']
    for lab in b.labels:
        x = b.center(lab)
        if rotate:
            out.append(f'<text class="ax" x="{x:.1f}" y="{f.ybot+14:.1f}" text-anchor="end" '
                       f'transform="rotate(-40 {x:.1f} {f.ybot+14:.1f})">{esc(lab)}</text>')
        else:
            out.append(f'<text class="ax" x="{x:.1f}" y="{f.ybot+18:.1f}" '
                       f'text-anchor="middle">{esc(lab)}</text>')
    return "".join(out)


def rule_h(f: Frame, sc: Scale, value: float, label: str) -> str:
    y = sc(value)
    return (f'<line x1="{f.x0}" y1="{y:.1f}" x2="{f.x1}" y2="{y:.1f}" stroke="{C["ink2"]}" '
            f'stroke-width="1.3" stroke-dasharray="5 3"/>'
            f'<text class="lab2" x="{f.x1}" y="{y-6:.1f}" text-anchor="end">{esc(label)}</text>')


def shade_x(f: Frame, sc: Scale, lo: float, hi: float, label: str) -> str:
    x0, x1 = sc(lo), sc(hi)
    return (f'<rect x="{x0:.1f}" y="{f.ytop}" width="{x1-x0:.1f}" '
            f'height="{f.ybot-f.ytop:.1f}" fill="{C["blue"]}" opacity="0.07"/>'
            f'<text class="ax" x="{x0+6:.1f}" y="{f.ytop+13}">{esc(label)}</text>')


# --------------------------------------------------------------------------- forms

def gapped_path(pts: Sequence[tuple[float, float] | None], colour: str,
                width: float = 2.0, dash: str | None = None) -> str:
    """None breaks the line. A year not in the record is never drawn through."""
    segs, cur = [], []
    for p in pts:
        if p is None:
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        segs.append(cur)
    d = " ".join("M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in s) for s in segs)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linejoin="round"{da}/>' if d else "")


def dumbbell(f: Frame, sc: Scale, b: Band, rows: Sequence[dict], lo_key: str,
             hi_key: str, label_key: str, lo_colour: str, hi_colour: str) -> str:
    out = []
    for r in rows:
        lab = r[label_key]
        x = b.center(lab)
        lo, hi = float(r[lo_key]), float(r[hi_key])
        out.append(f'<line x1="{x:.1f}" y1="{sc(lo):.1f}" x2="{x:.1f}" y2="{sc(hi):.1f}" '
                   f'stroke="{C["ink2"]}" stroke-width="1.2"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{sc(hi):.1f}" r="4" fill="none" '
                   f'stroke="{hi_colour}" stroke-width="1.8"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{sc(lo):.1f}" r="4" fill="{lo_colour}"/>')
    return "".join(out)


def spans(f: Frame, sc: Scale, rows: Sequence[dict], start_key: str, end_key: str,
          label_key: str, open_start_key: str | None = None) -> str:
    """Horizontal term bars. Bar length is the term, to scale."""
    out = []
    n = len(rows)
    step = (f.ybot - f.ytop) / (n + 1)
    for i, r in enumerate(rows, 1):
        y = f.ytop + step * i
        x0, x1 = sc(float(r[start_key])), sc(float(r[end_key]))
        openish = open_start_key and str(r.get(open_start_key, "")).strip().lower() in ("1", "yes", "true")
        out.append(f'<rect x="{x0:.1f}" y="{y-7:.1f}" width="{max(x1-x0,1):.1f}" height="14" '
                   f'rx="3" fill="{C["blue"]}" opacity="{0.32 if openish else 0.85}"/>')
        if openish:
            out.append(f'<text class="ax" x="{x0-5:.1f}" y="{y+4:.1f}" text-anchor="end">'
                       f'start not obtained</text>')
        out.append(f'<text class="lab2" x="{f.x0}" y="{y-12:.1f}">{esc(r[label_key])}</text>')
    return "".join(out)


def dot_plot(f: Frame, sc: Scale, b: Band, rows: Sequence[dict], value_key: str,
             label_key: str, grade_key_fn: Callable[[dict], str],
             plot_key: str = "plot") -> str:
    out = []
    for r in rows:
        lab = r[label_key]
        y = b.center(lab)
        v = float(r[value_key])
        drawn = (r.get(plot_key) or "plot").strip() == "plot"
        if drawn:
            out.append(mark(grade_key_fn(r), C["blue"], sc(v), y, r=5))
            out.append(f'<text class="val" x="{sc(v):.1f}" y="{y-11:.1f}" '
                       f'text-anchor="middle">${v:.2f}</text>')
        else:
            # annotated beside the axis, never plotted as a value
            out.append(f'<text class="ax" x="{f.x1}" y="{y+4:.1f}" text-anchor="end" '
                       f'fill="{C["muted"]}">${v:.2f} &#8212; annotated, not plotted</text>')
        out.append(f'<text class="lab2" x="{f.x0-8}" y="{y+4:.1f}" text-anchor="end">'
                   f'{esc(lab)}</text>')
    return "".join(out)


def ranked_bars(f: Frame, sc: Scale, b: Band, rows: Sequence[dict], value_key: str,
                label_key: str, fmt: Callable[[float], str] = lambda v: f"{v:,.0f}") -> str:
    """Horizontal bars from a zero baseline. No exceptions to the baseline."""
    out = []
    x_zero = sc(0)
    for r in rows:
        y = b.center(r[label_key])
        v = float(r[value_key])
        out.append(f'<rect x="{min(x_zero, sc(v)):.1f}" y="{y-9:.1f}" '
                   f'width="{abs(sc(v)-x_zero):.1f}" height="18" fill="{C["blue"]}" opacity="0.85"/>')
        out.append(f'<text class="val" x="{sc(v)+6:.1f}" y="{y+4:.1f}">{esc(fmt(v))}</text>')
        out.append(f'<text class="lab2" x="{f.x0-8}" y="{y+4:.1f}" text-anchor="end">'
                   f'{esc(r[label_key])}</text>')
    return "".join(out)


def stacked_bars(f: Frame, sc: Scale, b: Band, cols: Sequence[str],
                 series: Sequence[tuple[str, dict, str]]) -> str:
    """series: (name, {col: value}, colour). Stacks in the order given."""
    out = []
    bw = min(b.step * 0.62, 34)
    base = {c: 0.0 for c in cols}
    zero = sc(0)
    for name, vals, colour in series:
        for c in cols:
            v = float(vals.get(c, 0) or 0)
            if not v:
                continue
            y1 = sc(base[c] + v)
            y0 = sc(base[c])
            out.append(f'<rect x="{b.center(c)-bw/2:.1f}" y="{min(y0,y1):.1f}" '
                       f'width="{bw:.1f}" height="{abs(y0-y1):.1f}" fill="{colour}"/>')
            base[c] += v
    out.append(f'<line x1="{f.x0}" y1="{zero:.1f}" x2="{f.x1}" y2="{zero:.1f}" stroke="{C["axis"]}"/>')
    return "".join(out)


# --------------------------------------------------------------------------- frames

@dataclass(frozen=True)
class Panel:
    title: str
    subtitle: str
    draw: Callable[[Frame, Scale], str]


def small_multiples(outer: Frame, panels: Sequence[Panel], shared: Scale,
                    ticks: Sequence[float], rules: Sequence[tuple[float, str]] = (),
                    fmt: Callable[[float], str] = lambda v: f"{v:g}") -> str:
    """Panels side by side on ONE scale.

    The same Scale object is handed to every panel, and a panel's draw callable
    receives only (frame, scale), so there is no route by which one panel can
    build a second scale. That is what makes the comparison honest, and the
    caption says so.
    """
    n = len(panels)
    gap = 26
    pw = (outer.x1 - outer.x0 - gap * (n - 1)) / n
    out = []
    for i, p in enumerate(panels):
        x0 = outer.x0 + i * (pw + gap)
        f = Frame(w=x0 + pw, h=outer.h, l=x0, r=0, t=outer.t, b=outer.b)
        out.append(f'<text class="lab" x="{x0}" y="{outer.t-12}">{esc(p.title)}</text>')
        out.append(f'<text class="ax" x="{x0}" y="{outer.t+2}">{esc(p.subtitle)}</text>')
        out.append(axis_y(f, shared, ticks, fmt, labels=(i == 0)))
        for v, lab in rules:
            out.append(rule_h(f, shared, v, lab if i == 0 else ""))
        out.append(p.draw(f, shared))
    return "".join(out)


def paired_panels(outer: Frame, left: Panel, right: Panel, shared: Scale,
                  ticks: Sequence[float], fmt=lambda v: f"{v:g}") -> str:
    return small_multiples(outer, [left, right], shared, ticks, fmt=fmt)


# --------------------------------------------------------------------------- mechanism

def flow_diagram(f: Frame, nodes: Sequence[dict], edges: Sequence[dict]) -> str:
    """The flow of funds, drawn so the two discretionary levers are the only
    dashed strokes on the page.

    A reader who reads nothing but the strokes sees two dashed arrows entering
    one solid stack. The rule is enforced, not merely intended: a mandatory
    node drawn dashed, or a discretionary edge drawn solid, stops the build.

    No red. The case rule forbids the words default, breach and violation, and
    colour obeys the same rule.
    """
    by_id = {n["node_id"]: n for n in nodes}
    # A designation is discretionary at its source: the money being designated is
    # what the Authority chooses. A deposit is discretionary at its destination:
    # the account being filled is what the Authority chooses. Check the end that
    # carries the decision, or the guard passes on the wrong evidence.
    for e in edges:
        if e["kind"] == "designation":
            end, node = "source", by_id.get(e["from_node"], {})
        elif e["kind"] == "discretionary_deposit":
            end, node = "target", by_id.get(e["to_node"], {})
        else:
            continue
        if (node.get("discretion") or "mandatory") == "mandatory":
            raise SystemExit(
                f'flow_diagram: edge {e["from_node"]}->{e["to_node"]} is drawn as '
                f'discretionary but its {end} is marked mandatory. Fix the data.')

    prio = sorted([n for n in nodes if n["kind"] == "priority"],
                  key=lambda n: int(n["priority_order"]))
    out = []
    lane_x = f.x0 + 210
    box_w, box_h, gap = 250, 26, 7
    top = f.ytop + 96

    # Revenues -> Net Revenues, the solid spine
    out.append(_box(lane_x, f.ytop, box_w, box_h, "Revenues", C["blue"], solid=True))
    out.append(_arrow(lane_x + box_w / 2, f.ytop + box_h, lane_x + box_w / 2, f.ytop + 40, False))
    out.append(f'<text class="ax" x="{lane_x+box_w/2+8:.0f}" y="{f.ytop+34:.0f}">'
               f'less operation and maintenance</text>')
    out.append(_box(lane_x, f.ytop + 44, box_w, box_h, "Net Revenues", C["blue"], solid=True))

    # Lever one: designations entering Net Revenues from the left, dashed
    out.append(_box(f.x0, f.ytop + 44, 170, box_h, "Other Pledged Revenues",
                    C["aqua"], solid=False))
    out.append(_arrow(f.x0 + 170, f.ytop + 44 + box_h / 2, lane_x, f.ytop + 44 + box_h / 2, True))
    out.append(f'<text class="ax" x="{f.x0}" y="{f.ytop+44+box_h+15:.0f}">'
               f'designated annually, at the Authority&#8217;s discretion</text>')

    # The ladder
    y = top
    for n in prio:
        order = int(n["priority_order"])
        is9 = order == 9
        disc = (n.get("discretion") or "mandatory") != "mandatory"
        out.append(f'<circle cx="{lane_x-16:.0f}" cy="{y+box_h/2:.0f}" r="10" '
                   f'fill="none" stroke="{C["axis"]}"/>')
        out.append(f'<text class="ax" x="{lane_x-16:.0f}" y="{y+box_h/2+4:.0f}" '
                   f'text-anchor="middle">{order}</text>')
        out.append(_box(lane_x, y, box_w, box_h, n["label"],
                        C["blue_lt"] if is9 else C["surface"], solid=not disc,
                        emphasis=is9))
        if is9:
            out.append(_arrow(lane_x + box_w + 74, y + box_h / 2, lane_x + box_w, y + box_h / 2, True))
            out.append(f'<text class="ax" x="{lane_x+box_w+80:.0f}" y="{y+box_h/2-4:.0f}">'
                       f'funded monthly, at the Authority&#8217;s discretion</text>')
            out.append(f'<text class="ax" x="{lane_x+box_w+80:.0f}" y="{y+box_h/2+10:.0f}">'
                       f'capped at 25% of annual debt service</text>')
        y += box_h + gap

    # The two brackets: what the test counts, and what the pledged revenue does alone
    bx = lane_x + box_w + 24
    y9 = top + (9 - 1) * (box_h + gap)
    out.append(_bracket(bx, f.ytop + 44, y9 + box_h, "the 1.25 test counts both"))
    out.append(_bracket(bx + 16, f.ytop + 44, f.ytop + 44 + box_h,
                        "pledged revenue alone", faint=True))
    return "".join(out)


def _box(x, y, w, h, label, fill, solid=True, emphasis=False) -> str:
    dash = "" if solid else ' stroke-dasharray="5 3"'
    sw = 2.0 if emphasis else 1.2
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" rx="4" '
            f'fill="{fill}" fill-opacity="{0.28 if emphasis else 0.14}" '
            f'stroke="{C["ink2"] if not emphasis else C["blue"]}" stroke-width="{sw}"{dash}/>'
            f'<text class="lab2" x="{x+10:.0f}" y="{y+h/2+4:.0f}">{esc(label)}</text>')


def _arrow(x1, y1, x2, y2, dashed) -> str:
    da = ' stroke-dasharray="5 3"' if dashed else ""
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{C["ink2"]}" stroke-width="1.4" marker-end="url(#ar)"{da}/>')


def _bracket(x, y0, y1, label, faint=False) -> str:
    op = 0.5 if faint else 1
    return (f'<path d="M {x:.0f},{y0:.0f} l 7,0 l 0,{y1-y0:.0f} l -7,0" fill="none" '
            f'stroke="{C["ink2"]}" stroke-width="1.2" opacity="{op}"/>'
            f'<text class="ax" x="{x+12:.0f}" y="{(y0+y1)/2+4:.0f}" opacity="{op}">'
            f'{esc(label)}</text>')


DEFS = ('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
        'markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{C["ink2"]}"/></marker></defs>')


def svg(f: Frame, aria: str, body: str) -> str:
    return (f'<svg viewBox="0 0 {f.w:.0f} {f.h:.0f}" role="img" '
            f'aria-label="{esc(aria)}">{DEFS}{body}</svg>')
