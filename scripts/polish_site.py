"""Add shared navigation and styling to generated site pages.

Quarto and rudu replace their HTML files on every run, so these additions live
here and are applied after each render. The operation is idempotent.
"""

from pathlib import Path
import sys


STYLESHEET = '<link rel="stylesheet" href="site.css" data-resource-site-style>'
DASHBOARD_LINKS = (
    '<a class="site-link" href="gadi_gdata_stocktake.html">Gdata stocktake</a>'
    '<a class="site-link" href="gadi_scratch_stocktake.html">Scratch stocktake</a>'
)
STOCKTAKE_NAV = '''<nav class="site-nav stocktake-nav" aria-label="Primary navigation" data-resource-site-nav>
  <a class="site-brand" href="dashboard.html">
    <img src="logo.png" alt="" width="36" height="36">
    <span>21st Century Weather <small>Gadi resources</small></span>
  </a>
  <div class="site-nav-links">
    <a href="dashboard.html">Dashboard</a>
    <a href="gadi_gdata_stocktake.html">Gdata</a>
    <a href="gadi_scratch_stocktake.html">Scratch</a>
  </div>
</nav>'''


def insert_once(html: str, needle: str, addition: str, label: str) -> str:
    if addition in html:
        return html
    if needle not in html:
        raise ValueError(f"Could not find {label} in generated HTML")
    return html.replace(needle, needle + addition, 1)


def polish(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    if STYLESHEET not in html:
        if "</head>" not in html:
            raise ValueError(f"Could not find head in {path}")
        html = html.replace("</head>", f"{STYLESHEET}\n</head>", 1)

    if path.name == "dashboard.html":
        html = insert_once(
            html,
            '<div class="quarto-dashboard-links">',
            DASHBOARD_LINKS,
            "Quarto dashboard links",
        )
    elif path.name in {"gadi_gdata_stocktake.html", "gadi_scratch_stocktake.html"}:
        if 'class="rudu-stocktake"' not in html:
            if "<body>" not in html:
                raise ValueError(f"Could not find rudu body in {path}")
            html = html.replace("<body>", '<body class="rudu-stocktake">', 1)
        if "data-resource-site-nav" not in html:
            html = insert_once(html, '<div class="wrap">', f"\n{STOCKTAKE_NAV}", "rudu wrap")
        current = "gadi_gdata_stocktake.html" if path.name.startswith("gadi_gdata") else "gadi_scratch_stocktake.html"
        link = f'<a href="{current}">'
        html = html.replace(link, f'<a href="{current}" aria-current="page">', 1)
    else:
        raise ValueError(f"Unsupported generated page: {path}")

    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: polish_site.py generated_page.html [...] ")
    for filename in sys.argv[1:]:
        polish(Path(filename))
