"""Build a cover-letter HTML in the resume's style.

  python3 tools/make_letter.py <body.txt> <out.html> "<recipient line>"

The body file is plain paragraphs separated by blank lines (greeting through sign-off).
Name and contact line come from me/config.json; the date is today's.
"""
import html
import json
import sys
from datetime import date
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / 'me' / 'config.json'

body_path, out_path, recipient = sys.argv[1:4]
cfg = json.loads(CONFIG.read_text())
paras = [p.strip() for p in open(body_path).read().split("\n\n") if p.strip()]
body = "\n".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paras)


def contact_item(item):
    if isinstance(item, str):
        return f"<span>{html.escape(item)}</span>"
    return f"<span><a href=\"{html.escape(item['href'])}\">{html.escape(item['text'])}</a></span>"


contact = "".join(contact_item(c) for c in cfg['contact'])
today = date.today()
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(cfg['name'])} – Cover Letter</title>
<style>
  @page {{ size: A4; margin: 18mm 20mm; }}
  body {{ margin: 0; font-family: "Noto Sans", "Ubuntu Sans", Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1d2329; }}
  a {{ color: inherit; text-decoration: none; }}
  h1 {{ font-size: 21pt; font-weight: 700; margin: 0 0 2pt; letter-spacing: -0.2pt; color: #12324f; }}
  .contact {{ font-size: 9pt; color: #444; padding-bottom: 8pt; border-bottom: 1.2pt solid #12324f; margin-bottom: 18pt; }}
  .contact span {{ white-space: nowrap; }}
  .contact span + span::before {{ content: "·"; margin: 0 5pt; color: #999; }}
  .meta {{ margin-bottom: 14pt; color: #444; }}
  p {{ margin: 0 0 10pt; }}
</style>
</head>
<body>
  <h1>{html.escape(cfg['name'])}</h1>
  <div class="contact">
    {contact}
  </div>
  <div class="meta">{today.day} {today:%B %Y}<br>{html.escape(recipient)}</div>
{body}
</body>
</html>
"""
open(out_path, "w").write(page)
