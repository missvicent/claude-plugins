"""Render a tracker JSON file into tracker.html, tracker.md and tracker.pdf.

Usage: python build.py <trackers/<feature>/tracker.json>

Writes the three files next to the JSON. The HTML has no <!doctype>/<head>
because the Artifact tool adds that skeleton at publish time; the PDF is printed
from a wrapped copy so Chrome doesn't render it in quirks mode.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STATUS = {"done": "Done", "wip": "In progress", "todo": "To do"}
SEVERITY = {"bad": "Must fix", "edge": "Edge case", "minor": "Cosmetic"}
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOG_CAP = 5  # entries kept per task; older ones fold into log_summary


def inline(text: str) -> str:
    """Escape HTML, then turn `backticks` into <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text))


def cap_logs(d: dict) -> bool:
    """Keep the last LOG_CAP entries per task; fold the rest into one
    `log_summary` line. Returns True when the data changed."""
    changed = False
    for t in d["tasks"]:
        log = t.get("log", [])
        if len(log) <= LOG_CAP:
            continue
        old, t["log"] = log[:-LOG_CAP], log[-LOG_CAP:]
        fails = [e for e in old if e.get("result") == "fail"]
        prev = t.get("log_summary", "")
        n_prev = int(m.group(1)) if (m := re.match(r"(\d+) earlier", prev)) else 0
        f_prev = int(m.group(1)) if (m := re.search(r"(\d+) failed", prev)) else 0
        last = fails[-1]["note"] if fails else ""
        t["log_summary"] = (
            f"{n_prev + len(old)} earlier checks, {f_prev + len(fails)} failed"
            + (f" (last: {last})" if last else "")
        )
        changed = True
    return changed


def tries(t: dict) -> str:
    """' · 3 tries' when a task has been checked more than once."""
    n = len(t.get("log", []))
    if m := re.match(r"(\d+) earlier", t.get("log_summary", "")):
        n += int(m.group(1))
    return f" · {n} tries" if n > 1 else ""


def owner(t: dict) -> str:
    """`you`, `agent · workflow` or `agent · subagent`; "" for old trackers."""
    if t.get("by") == "agent":
        return f"agent · {t.get('run_as', 'workflow')}"
    return t.get("by", "")


def check_text(c: dict) -> str:
    """One line for a task's check: `cmd → expect`, or the review list."""
    if c.get("kind") == "review":
        return "review: " + "; ".join(c.get("look_for", []))
    line = c.get("cmd", "")
    if c.get("expect"):
        line += f" → {c['expect']}"
    return line + (" (asks first)" if c.get("kind") == "ask" else "")


def progress(tasks: list[dict]) -> str:
    required = [t for t in tasks if not t.get("optional")]
    done = sum(t["status"] == "done" for t in required)
    wip = sum(t["status"] == "wip" for t in required)
    text = f"{done} of {len(required)} done"
    return text + (f" · {wip} in progress" if wip else "")


CSS = """
:root {
  --bg: #f6f7f5; --fg: #1d2420; --muted: #5d6a63; --line: #d9dfdb;
  --done: #2f7a4f; --todo: #a35b12; --wip: #2b5fa8; --bad: #b3261e; --chip: #e9ede9;
  --sans: "IBM Plex Sans", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #141917; --fg: #e3e9e5; --muted: #95a39b; --line: #2c3530;
  --done: #6cc492; --todo: #e5a25a; --wip: #7fa8e8; --bad: #f08a80; --chip: #212825;
  color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #141917; --fg: #e3e9e5; --muted: #95a39b; --line: #2c3530;
  --done: #6cc492; --todo: #e5a25a; --wip: #7fa8e8; --bad: #f08a80; --chip: #212825;
  color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 15px/1.5 var(--sans); }
main { max-width: 760px; margin: 0 auto; padding-inline: 16px; padding-block: 40px; }
h1 { font-size: 1.5rem; margin: 0 0 4px; text-wrap: balance; }
h2 { font-size: .8rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--muted); margin: 32px 0 4px; }
.eyebrow { font-family: var(--mono); font-size: .78rem; color: var(--muted);
  margin: 0 0 8px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.tag { font-size: .7rem; background: var(--chip); padding: 1px 7px; border-radius: 4px; }
.brief { max-width: 65ch; margin: 8px 0 16px; }
.meta { display: flex; flex-wrap: wrap; gap: 8px 28px; margin: 0; }
.meta dt { font-size: .7rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--muted); }
.meta dd { margin: 2px 0 0; font-variant-numeric: tabular-nums; }
.wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: .72rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--muted); font-weight: 600; padding: 8px 10px;
  border-bottom: 1px solid var(--line); }
td { padding: 12px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
td.n { font-family: var(--mono); color: var(--muted); font-variant-numeric: tabular-nums;
  width: 2ch; }
code { font-family: var(--mono); font-size: .85em; background: var(--chip);
  padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere; }
.det { margin: 6px 0 0; padding-left: 18px; color: var(--muted); font-size: .85rem;
  display: grid; gap: 3px; }
.det li.now { color: var(--wip); }
.pill { display: inline-block; font-family: var(--mono); font-size: .72rem;
  padding: 2px 8px; border-radius: 999px; border: 1px solid currentColor;
  white-space: nowrap; }
.done { color: var(--done); } .todo, .edge { color: var(--todo); }
.wip { color: var(--wip); } .bad { color: var(--bad); } .minor { color: var(--muted); }
tr.is-done td:not(:last-child) { color: var(--muted); }
.det li.goal, .det li.check { color: var(--fg); }
.det b { font-weight: 600; }
.by { display: inline-block; font-family: var(--mono); font-size: .68rem;
  background: var(--chip); padding: 1px 7px; border-radius: 4px; margin-left: 6px;
  vertical-align: 1px; white-space: nowrap; }
.ask { color: var(--todo); }
details.more { margin: 6px 0 0 18px; font-size: .85rem; color: var(--muted); }
details.more summary { cursor: pointer; }
details.more ol, details.more ul { margin: 4px 0; padding-left: 18px; }
.decisions { border: 1px solid var(--todo); border-radius: 8px; padding: 4px 14px;
  margin: 16px 0 0; }
.decisions li { margin: 6px 0; }
.order { margin: 20px 0 0; max-width: 65ch; color: var(--muted); }
.order strong { color: var(--fg); }
@media print { body { font-size: 12px; } main { padding-block: 0; }
  tr { break-inside: avoid; } }
"""

FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500"
    '&display=swap">'
)


def render_html(d: dict) -> str:
    out = [f"<title>{html.escape(d['title'])}</title>", FONTS, f"<style>{CSS}</style>"]
    out.append("<main>")
    if d.get("eyebrow") or d.get("tags"):
        tags = "".join(
            f' <span class="tag">{html.escape(t)}</span>' for t in d.get("tags", [])
        )
        out.append(f'<p class="eyebrow">{html.escape(d.get("eyebrow", ""))}{tags}</p>')
    out.append(f"<h1>{inline(d.get('heading', d['title']))}</h1>")
    if d.get("brief"):
        out.append(f'<p class="brief">{inline(d["brief"])}</p>')
    meta = {
        **d.get("meta", {}),
        "Progress": f"{progress(d['tasks'])} · as of {d['as_of']}",
    }
    out.append('<dl class="meta">')
    out += [
        f"<div><dt>{html.escape(k)}</dt><dd>{inline(v)}</dd></div>"
        for k, v in meta.items()
    ]
    out.append("</dl>")

    decisions = d.get("decisions", [])
    open_d = [x for x in decisions if x.get("status") != "decided"]
    if open_d:
        out.append("<h2>Open decisions</h2>")
        out.append('<div class="decisions"><ul>')
        for x in open_d:
            opts = " · ".join(inline(o) for o in x.get("options", []))
            where = f" (blocks task {x['task']})" if x.get("task") else ""
            out.append(f"<li><b>{inline(x['question'])}</b>{where}<br>{opts}</li>")
        out.append("</ul></div>")

    out.append("<h2>Remaining work</h2>")
    out.append(
        '<div class="wrap"><table><thead><tr><th>#</th><th>Task</th>'
        "<th>Status</th></tr></thead><tbody>"
    )
    for i, t in enumerate(d["tasks"], 1):
        label = ("Optional: " if t.get("optional") else "") + t["task"]
        chip = f'<span class="by">{html.escape(owner(t))}</span>' if owner(t) else ""
        items = []
        if t.get("goal"):
            items.append(f'<li class="goal"><b>Goal:</b> {inline(t["goal"])}</li>')
        if t.get("check"):
            ask = (
                ' class="check ask"'
                if t["check"].get("kind") == "ask"
                else ' class="check"'
            )
            items.append(
                f"<li{ask}><b>Check:</b> {inline(check_text(t['check']))}</li>"
            )
        items += [f"<li>{inline(x)}</li>" for x in t.get("details", [])]
        if t.get("now"):
            items.append(f'<li class="now">{inline(t["now"])}</li>')
        det = f'<ul class="det">{"".join(items)}</ul>' if items else ""
        more = ""
        if t.get("shapes") or t.get("steps"):
            parts = []
            if t.get("shapes"):
                parts.append("<b>Shapes</b><ul>")
                parts += [f"<li>{inline(x)}</li>" for x in t["shapes"]]
                parts.append("</ul>")
            if t.get("steps"):
                parts.append("<b>Steps</b><ol>")
                parts += [f"<li>{inline(x)}</li>" for x in t["steps"]]
                parts.append("</ol>")
            more = (
                '<details class="more"><summary>Shapes and steps</summary>'
                + "".join(parts)
                + "</details>"
            )
        cls = ' class="is-done"' if t["status"] == "done" else ""
        pill = (
            f'<span class="pill {t["status"]}">{STATUS[t["status"]]}{tries(t)}</span>'
        )
        out.append(
            f'<tr{cls}><td class="n">{i}</td><td>{inline(label)}{chip}{det}{more}</td>'
            f"<td>{pill}</td></tr>"
        )
    out.append("</tbody></table></div>")

    decided = [x for x in decisions if x.get("status") == "decided"]
    if decided:
        out.append("<h2>Decisions made</h2>")
        out.append('<ul class="det">')
        out += [
            f"<li><b>{inline(x['question'])}</b> → {inline(x.get('answer', ''))}</li>"
            for x in decided
        ]
        out.append("</ul>")

    if d.get("problems"):
        out.append(f"<h2>{inline(d.get('problems_heading', 'Open problems'))}</h2>")
        out.append(
            '<div class="wrap"><table><thead><tr><th>Problem</th><th>Where</th>'
            "<th>Severity</th></tr></thead><tbody>"
        )
        for p in d["problems"]:
            sev = p.get("severity", "bad")
            out.append(
                f"<tr><td>{inline(p['problem'])}</td><td>{inline(p['where'])}</td>"
                f'<td><span class="pill {sev}">{SEVERITY[sev]}</span></td></tr>'
            )
        out.append("</tbody></table></div>")

    if d.get("order"):
        out.append(
            f'<p class="order"><strong>Suggested order:</strong> {inline(d["order"])}</p>'
        )
    out.append("</main>")
    return "\n".join(out) + "\n"


def render_md(d: dict) -> str:
    cell = lambda s: s.replace("|", "\\|")  # noqa: E731
    lines = [f"# {d.get('heading', d['title'])}", ""]
    if d.get("eyebrow") or d.get("tags"):
        lines += [
            " · ".join([d.get("eyebrow", ""), *d.get("tags", [])]).strip(" ·"),
            "",
        ]
    if d.get("brief"):
        lines += [d["brief"], ""]
    meta = {
        **d.get("meta", {}),
        "Progress": f"{progress(d['tasks'])} · as of {d['as_of']}",
    }
    lines += [f"- **{k}:** {v}" for k, v in meta.items()] + [""]
    decisions = d.get("decisions", [])
    open_d = [x for x in decisions if x.get("status") != "decided"]
    if open_d:
        lines += ["## Open decisions", ""]
        for x in open_d:
            where = f" (blocks task {x['task']})" if x.get("task") else ""
            lines.append(f"- **{x['question']}**{where}")
            lines += [f"  - {o}" for o in x.get("options", [])]
        lines.append("")
    lines += ["## Remaining work", ""]
    lines += ["| # | Task | Status |", "|---|---|---|"]
    for i, t in enumerate(d["tasks"], 1):
        label = ("Optional: " if t.get("optional") else "") + t["task"]
        if owner(t):
            label += f" [{owner(t)}]"
        subs = []
        if t.get("goal"):
            subs.append(f"*Goal:* {t['goal']}")
        if t.get("check"):
            subs.append(
                f"*Check ({t['check'].get('kind', 'run')}):* {check_text(t['check'])}"
            )
        subs += t.get("details", [])
        subs += [f"*Shape:* {x}" for x in t.get("shapes", [])]
        subs += [f"*Step {n}:* {x}" for n, x in enumerate(t.get("steps", []), 1)]
        if t.get("now"):
            subs.append(f"*Now:* {t['now']}")
        body = cell(label) + "".join(f"<br>• {cell(s)}" for s in subs)
        lines.append(f"| {i} | {body} | {STATUS[t['status']]}{tries(t)} |")
    if d.get("problems"):
        lines += ["", f"## {d.get('problems_heading', 'Open problems')}", ""]
        lines += ["| Problem | Where | Severity |", "|---|---|---|"]
        lines += [
            f"| {cell(p['problem'])} | {cell(p['where'])} | "
            f"{SEVERITY[p.get('severity', 'bad')]} |"
            for p in d["problems"]
        ]
    decided = [x for x in decisions if x.get("status") == "decided"]
    if decided:
        lines += ["", "## Decisions made", ""]
        lines += [f"- **{x['question']}** → {x.get('answer', '')}" for x in decided]
    if d.get("order"):
        lines += ["", f"**Suggested order:** {d['order']}"]
    return "\n".join(lines) + "\n"


def render_pdf(page: str, out: Path) -> bool:
    chrome = CHROME if Path(CHROME).exists() else shutil.which("google-chrome")
    if not chrome:
        print("no Chrome found; skipped PDF", file=sys.stderr)
        return False
    wrapped = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width">'
        "</head><body>" + page + "</body></html>"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(wrapped)
    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out}",
            f"file://{f.name}",
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    Path(f.name).unlink()
    return out.exists()


def main(path: str, pdf: bool = False) -> None:
    src = Path(path)
    d = json.loads(src.read_text(encoding="utf-8"))
    if cap_logs(d):
        src.write_text(
            json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    page = render_html(d)
    (src.parent / "tracker.html").write_text(page, encoding="utf-8")
    (src.parent / "tracker.md").write_text(render_md(d), encoding="utf-8")
    # PDF launches headless Chrome, so it only runs when asked for (--pdf)
    pdf_ok = pdf and render_pdf(page, src.parent / "tracker.pdf")
    print(
        f"wrote tracker.html, tracker.md{', tracker.pdf' if pdf_ok else ''} in {src.parent}"
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    main(next(a for a in args if a != "--pdf"), pdf="--pdf" in args)
