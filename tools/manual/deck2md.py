"""Convert a Slides deck folder (deck.json + slides/*.html) into a GitHub Markdown manual.
usage: deck2md.py <deck_project_dir> <blobmap.txt> <out.md> <title>
blobmap lines: <blob id> <image file name>  -> referenced as images/<file>
"""
import json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

proj, blobmap, out, title = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4]
bmap = dict(l.split() for l in open(blobmap) if l.strip())
deck = json.loads((proj / "deck.json").read_text())


def txt(el):
    """inline text with **bold** / *italic*, collapsed whitespace"""
    parts = []
    for c in el.children:
        if isinstance(c, NavigableString):
            parts.append(str(c))
        elif c.name == "br":
            parts.append(" ")
        elif c.name == "b":
            parts.append(f"**{txt(c).strip()}**")
        elif c.name == "i":
            parts.append(f"*{txt(c).strip()}*")
        else:
            parts.append(txt(c))
    s = "".join(parts).replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def style(el):
    return (el.get("style") or "").replace(" ", "")


def img_md(img):
    bid = img["src"].rsplit("/", 1)[-1]
    f = bmap.get(bid)
    if not f:
        raise SystemExit(f"no image for blob {bid}")
    return f"![{img.get('alt', '')}](images/{f})"


def table_md(t):
    rows = [[txt(c) for c in tr.find_all(["th", "td"])] for tr in t.find_all("tr")]
    aligns = []
    for c in t.find("tr").find_all(["th", "td"]):
        aligns.append("---:" if "text-align:right" in style(c) else "---")
    lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(aligns) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def is_footer(el):
    s = style(el)
    return "position:absolute" in s and "bottom:" in s


def render_block(el, md):
    """walk content of a slide in reading order"""
    for c in el.children:
        if isinstance(c, NavigableString) or c.name in (None, "aside"):
            continue
        s = style(c)
        if is_footer(c):
            continue
        if c.name == "div" and "position:absolute" in s and not c.get_text(strip=True):
            continue  # decorative bar
        if c.name == "img":
            md.append(img_md(c))
        elif c.name == "table":
            md.append(table_md(c))
        elif c.name in ("ul", "ol"):
            for i, li in enumerate(c.find_all("li"), 1):
                md.append((f"{i}. " if c.name == "ol" else "- ") + txt(li))
            md.append("")
        elif c.name == "h3":
            md.append(f"#### {txt(c)}")
        elif c.name == "p":
            t = txt(c)
            if t:
                md.append(t)
        elif c.name == "div":
            if "border-left:6px" in s:  # tip / warning
                kind = "WARNING" if "#E8752A" in (c.get("style") or "") else "TIP"
                body = " ".join(txt(p) for p in c.find_all("p"))
                md.append(f"> [!{kind}]\n> {body}")
            elif "YOU NEED" in c.get_text() and not c.find("div"):
                ps = c.find_all("p")
                md.append(f"**You need:** {txt(ps[-1])}")
            elif c.find("x-icon") and not c.find("div"):
                md.append(f"- [ ] {txt(c.find('p'))}")
            elif "border-bottom:2px" in s and len(c.find_all("p")) == 2 and not c.find("div"):
                a, b = c.find_all("p")
                md.append(f"- {txt(a)} — {txt(b)}" if len(txt(a)) > 3 else f"{txt(a)}. {txt(b)}")
            else:
                render_block(c, md)
        md.append("")


md = [f"# {title}", ""]
skip_contents = True
for sid in deck["order"]:
    soup = BeautifulSoup((proj / "slides" / f"{sid}.html").read_text(), "html.parser")
    sec = soup.find("section")
    if sid == "contents":
        continue
    if sid == "cover":
        for p in sec.find_all("p"):
            if not is_footer(p) and "letter-spacing:4px" not in style(p):
                md += [txt(p), ""]
        md += [img_md(sec.find("img")), ""]
        md += ["*Colour code in every step: **orange** = the part you are working on now, **blue** = screws, inserts, "
               "magnets and other hardware, grey = parts already fitted.*", "", "---", ""]
        continue
    if sid.startswith("div_"):
        num = sec.find("p").get_text(strip=True)
        md += [f"## {num} · {txt(sec.find('h1'))}", "", txt(sec.find_all("p")[1]), "", "---", ""]
        continue
    if sid == "closing":
        md += ["---", "", f"## {txt(sec.find('h1'))}", ""]
        for p in sec.find_all("p"):
            if not is_footer(p):
                md += [txt(p), ""]
        md += [img_md(sec.find("img")), ""]
        continue
    hdr = sec.find("div")
    eyebrow = hdr.find("p").get_text(strip=True)
    h = txt(hdr.find(["h2", "h1"]))
    md += [f"### {h}", "", f"<sub>{eyebrow}</sub>", ""]
    body = []
    for c in sec.children:
        if c is hdr or isinstance(c, NavigableString):
            continue
        wrap = BeautifulSoup("<div></div>", "html.parser").div
        wrap.append(c.__copy__())
        render_block(wrap, body)
    # collapse blank runs
    clean = []
    for l in body:
        if l == "" and (not clean or clean[-1] == ""):
            continue
        clean.append(l)
    md += clean + ["---", ""]

text = "\n".join(md)
text = re.sub(r"\n{3,}", "\n\n", text).replace("\n---\n\n---\n", "\n---\n")
out.write_text(text.strip() + "\n")
print("wrote", out, len(text.splitlines()), "lines")
