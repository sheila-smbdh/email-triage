"""Build Jordan's setter scorecard (HTML + PNG) from a metrics JSON file.

Usage: python3 build.py metrics.json OUT_DIR

Writes OUT_DIR/jordan-scorecard.html (page content for the artifact) and
OUT_DIR/jordan-scorecard-<measured_on>.png. Targets and colours live here, not in
the metrics file, so a daily run cannot change them. See README.md for the
metrics schema and how each number is counted.
"""
import datetime as dt
import html
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

# key: (tile name, target % or None for a tracked tile)
KPIS = {
    "reply2h": ("Reply within 2 business hours", 80),
    "sameday_call": ("Same-day call when a number is given", 80),
    "held": ("Leads to held setter call", 30),
    "booked_live": ("Next call booked before hanging up", 80),
    "set_closer": ("Set to a closer", None),
    "closer_show": ("Closer show rate", None),
}
ROWS = [
    ("Speed to lead and booking", ["reply2h", "sameday_call", "held"]),
    ("On the call", ["booked_live", "set_closer", "closer_show"]),
]
PILL = {"hit": "Hit", "close": "Close", "miss": "Missed", "track": "Tracking"}


def esc(s):
    return html.escape(str(s), quote=False)


def day(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d:%b} {d.day}"


def pct(num, den):
    return round(100 * num / den) if den else None


def status(p, target):
    if target is None or p is None:
        return "track"
    if p >= target:
        return "hit"
    if p >= 0.75 * target:
        return "close"
    return "miss"


def detail(key, k):
    num, den = k.get("num", 0), k.get("den", 0)
    if key == "reply2h":
        s = f"{num} of {den} leads"
        if k.get("median_hours") is not None:
            s += f". Median about {k['median_hours']:g} business hours"
        return s
    if key == "sameday_call":
        return f"{num} of {den} leads with a number"
    if key == "held":
        return f"{num} of {den} leads"
    if key == "booked_live":
        s = f"{num} of {den} held calls ended with a closer call or callback on the calendar"
        if k.get("excluded_not_fit"):
            n = k["excluded_not_fit"]
            s += f'. {n} clear "not a fit" call{"s" if n != 1 else ""} excluded'
        return s
    if key == "set_closer":
        s = f"{num} of {den} held calls"
        if k.get("names"):
            s += f" ({', '.join(k['names'])})"
        return s
    if key == "closer_show":
        s = f"{num} of {den} closer calls held" if den else "No closer call due yet"
        if k.get("upcoming"):
            s += f". Upcoming: {k['upcoming']}"
        return s
    return f"{num} of {den}"


def tile(key, k):
    name, target = KPIS[key]
    p = pct(k.get("num", 0), k.get("den", 0))
    st = status(p, target)
    v = f"{p}%" if p is not None else "n/a"
    width = min(p or 0, 100)
    marker = f'<b style="left:{min(target, 99)}%"></b>' if target is not None else ""
    if target is not None:
        foot = f"Target {target}%"
    elif key == "closer_show":
        foot = "Guardrail, no target"
    else:
        foot = "Tracked, not a target"
    return (f'<div class="kpi {st}"><div class="nm">{esc(name)}</div><div class="v">{v}</div>'
            f'<div class="of">{esc(detail(key, k))}</div>'
            f'<div class="tbar"><i style="width:{width}%"></i>{marker}</div>'
            f'<div class="st"><span>{foot}</span><span class="pill">{PILL[st]}</span></div></div>')


def build(m):
    css = (HERE / "style.css").read_text()
    wins = "".join(f"<li>{esc(w)}</li>" for w in m.get("wins", [])) or "<li>No wins logged.</li>"
    fixes = "".join(f"<li>{esc(f)}</li>" for f in m.get("fixes", [])) or "<li>Nothing to fix.</li>"
    rows = []
    for i, (label, keys) in enumerate(ROWS):
        style = ' style="margin-bottom:12px"' if i == 0 else ""
        tiles = "\n      ".join(tile(k, m["kpis"].get(k, {})) for k in keys)
        rows.append(f'    <div class="group">{label}</div>\n    <div class="kpis"{style}>\n      {tiles}\n    </div>')
    notes = "".join(f"<span>{esc(n)}</span>" for n in m.get("notes", []))
    return f"""<title>Jordan's Setter Scorecard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap">
<style>
{css}</style>

<div class="card">
  <header>
    <div class="eyebrow">Helen email leads · setter scorecard · v1</div>
    <h1>Jordan's last two weeks</h1>
    <div class="meta">Leads forwarded {day(m['window_start'])} to {day(m['window_end'])}, measured on {day(m['measured_on'])}.</div>
  </header>
  <div class="bl">
    <div class="callout win">
      <div class="k">Wins</div>
      <ol class="list">{wins}</ol>
    </div>
    <div class="callout fix">
      <div class="k">Fixes for this week</div>
      <ol class="list">{fixes}</ol>
    </div>
  </div>

  <section>
    <h2>Your numbers vs target</h2>
    <p class="lead">Green: you hit the target. Yellow: almost there (75% of the target or more). Red: you missed it. Blue: tracked, no target. The black line on each bar is the target.</p>
{chr(10).join(rows)}
  </section>
  <div class="foot">{notes}<span>Business hours are 9am to 5pm Jordan's time (MT). Rolling 2-week window of Helen's forwards. Sources: Email Triage Tracker (JordanK tab), Close calls, meetings, notes and emails.</span></div>
</div>
"""


def render_png(page_html, out_png):
    from playwright.sync_api import sync_playwright
    doc = ('<!doctype html><html><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
           f'<body style="margin:0">{page_html}</body></html>')
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": 820, "height": 900}, device_scale_factor=2, color_scheme="light")
        pg.set_content(doc, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        pg.locator(".card").screenshot(path=str(out_png))
        b.close()


def main():
    m = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    page = build(m)
    (out / "jordan-scorecard.html").write_text(page)
    png = out / f"jordan-scorecard-{m['measured_on']}.png"
    render_png(page, png)
    print(out / "jordan-scorecard.html")
    print(png)


if __name__ == "__main__":
    main()
