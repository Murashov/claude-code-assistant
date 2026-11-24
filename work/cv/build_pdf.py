"""Build the 2-page PDF CV from cv-2page.html.

Usage (reportlab is not installed system-wide, so use a venv):
    python3 -m venv /path/to/venv && /path/to/venv/bin/pip install reportlab
    /path/to/venv/bin/python work/cv/build_pdf.py

Reads work/cv/cv-2page.html, writes work/cv/Artyom-Murashov-CV.pdf.
Layout: a dark header band with key figures, a shaded sidebar (profile,
highlights, languages and contact on page 1; impact, skills and education on
page 2) and the experience in the main column.
Notes marked class="todo" in the HTML are left out of the PDF.
"""
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                NextPageTemplate, PageTemplate, Paragraph)

HERE = Path(__file__).parent
SRC = HERE / "cv-2page.html"
OUT = HERE / "Artyom-Murashov-CV.pdf"

# Colors sampled from reference/Svetlana-Anastasova-CV.pdf (Art, 2026-11-24).
BAND, INK, MUTED, LINE, PANEL, ACCENT, DOT = (HexColor(c) for c in (
    "#171a22", "#1c1f26", "#6c7486", "#d9dce2", "#f5f6f8", "#7b3a6c", "#c4589a"))
ON_BAND, ON_BAND_MUTED, BAND_LINE = (HexColor(c) for c in ("#e3e5ea", "#aab0be", "#4a4f5c"))
REG, SEMI, BOLD = "SourceSans3-Regular", "SourceSans3-SemiBold", "SourceSans3-Bold"

W, H = A4
MARGIN_X = 38
BAND_1, BAND_2 = 162, 44        # header band height on page 1 and on page 2
GAP_TOP = 18                    # band to content
FOOT = 40                       # bottom of the content area
SIDE_W, GUTTER, SIDE_PAD = 154, 16, 9
MAIN_X = MARGIN_X + SIDE_W + GUTTER
MAIN_W = W - MARGIN_X - MAIN_X
SIZE, LEAD = 8.9, 11.3          # main column body
S_SIZE, S_LEAD = 8.5, 11.2      # sidebar body


def inline(fragment):
    """Inline HTML to reportlab paragraph markup."""
    fragment = re.sub(r'<span class="todo">.*?</span>', "", fragment, flags=re.S)
    fragment = re.sub(r"</?strong>", lambda m: m.group(0).replace("strong", "b"), fragment)
    fragment = re.sub(r"</?span[^>]*>", "", fragment)
    return " ".join(fragment.split())


def plain(fragment):
    return re.sub(r"<[^>]+>", "", inline(fragment)).replace("&amp;", "&")


def one(pattern, src):
    return re.search(pattern, src, re.S).group(1)


def blocks(fragment):
    return [(tag, inline(inner)) for tag, inner in
            re.findall(r"<(p|li)>(.*?)</\1>", fragment, flags=re.S)]


def labelled(fragment):
    """'<strong>Label:</strong> text' items as (label, text) pairs."""
    out = []
    for _, item in blocks(fragment):
        label, text = re.match(r"<b>(.*?):</b>\s*(.*)", item).groups()
        out.append((label, text[0].upper() + text[1:]))
    return out


def figures(cls, src):
    return [(plain(v), [inline(x) for x in rest.split("<br>")]) for v, rest in
            re.findall(r"<li><b>(.*?)</b>(.*?)</li>", one(rf'<ul class="{cls}">(.*?)</ul>', src), re.S)]


def read():
    src = SRC.read_text(encoding="utf-8")
    src = src[src.index('<div class="page">'):]
    cv = {
        "name": plain(one(r"<h1>(.*?)</h1>", src)),
        "headline": plain(one(r'<div class="headline">(.*?)</div>', src)).split(" | "),
        "subline": plain(one(r'<div class="subline">(.*?)</div>', src)),
        "metrics": figures("metrics", src),
        "impact": figures("impact", src),
    }
    contact = one(r'<div class="contact">(.*?)</div>', src)
    cv["location"] = plain(contact).split(" · ")[0]
    cv["links"] = re.findall(r'<a href="(.*?)">(.*?)</a>', contact)
    summary = one(r"<h2>Summary</h2>(.*?)<h2>", src)
    cv["profile"] = inline(one(r"<p>(.*?)</p>", summary))
    cv["highlights"] = labelled(one(r"<ul>(.*?)</ul>", summary))
    cv["jobs"] = []
    for cls, inner in re.findall(r'<section class="(job[^"]*)" id="\w+">(.*?)</section>', src, re.S):
        title, company = inline(one(r'<span class="role">(.*?)</span>', inner)).split(" · ", 1)
        cv["jobs"].append(dict(early="early" in cls, title=title, company=company,
                               meta=inline(one(r'<span class="meta">(.*?)</span>', inner)),
                               blocks=blocks(inner)))
    cv["skills"] = labelled(one(r"<h2>Skills</h2>(.*?)<h2>", src))
    tail = src[src.index("<h2>Education and languages</h2>"):]
    cv["school"], cv["degree"] = inline(one(r'<span class="role">(.*?)</span>', tail)).split(" · ", 1)
    cv["years"] = inline(one(r'<span class="meta">(.*?)</span>', tail))
    cv["languages"] = [re.match(r"(.*) \((.*)\)", x).groups()
                       for x in plain(one(r"<p>(.*?)</p>", tail)).split(" · ")]
    return cv


def fonts():
    for name in (REG, SEMI, BOLD, "SourceSans3-Italic"):
        pdfmetrics.registerFont(TTFont(name, str(HERE / "fonts" / f"{name}.ttf")))
    pdfmetrics.registerFontFamily(REG, normal=REG, bold=BOLD,
                                  italic="SourceSans3-Italic", boldItalic=BOLD)


class Label(Flowable):
    """One line of letter-spaced capitals, optionally with a rule under it."""

    def __init__(self, text, size, color, before=0, after=0, rule=False):
        super().__init__()
        self.text, self.size, self.color, self.rule = text.upper(), size, color, rule
        self.spaceBefore, self.spaceAfter = before, after

    def wrap(self, avail_w, avail_h):
        self.width = avail_w
        self.height = self.size * 1.15 + (5 if self.rule else 0)
        return self.width, self.height

    def draw(self):
        c = self.canv
        t = c.beginText(0, 6.5 if self.rule else 1)
        t.setFont(BOLD, self.size)
        t.setCharSpace(self.size * 0.09)
        t.setFillColor(self.color)
        t.textOut(self.text)
        c.drawText(t)
        if self.rule:
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            c.line(0, 0.4, self.width, 0.4)


class Figure(Flowable):
    """A large figure with a caption, for the sidebar."""

    def __init__(self, value, caption, style, rule):
        super().__init__()
        self.value, self.rule = value, rule
        self.caption = Paragraph(caption, style)
        self.spaceAfter = 7

    def wrap(self, avail_w, avail_h):
        self.width = avail_w
        self.cap_h = self.caption.wrap(avail_w, avail_h)[1]
        self.height = 15 + self.cap_h + (7 if self.rule else 0)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFont(BOLD, 12.5)
        c.setFillColor(ACCENT)
        c.drawString(0, self.height - 11, self.value)
        self.caption.drawOn(c, 0, self.height - 15 - self.cap_h)
        if self.rule:
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            c.line(0, 0, self.width, 0)


def styles():
    body = ParagraphStyle("body", fontName=REG, fontSize=SIZE, leading=LEAD,
                          textColor=INK, spaceBefore=2, spaceAfter=1)
    side = ParagraphStyle("side", fontName=REG, fontSize=S_SIZE, leading=S_LEAD,
                          textColor=INK, spaceAfter=3)
    return {
        "p": body,
        "li": ParagraphStyle("li", parent=body, leftIndent=9, bulletIndent=0.5,
                             bulletColor=DOT, spaceBefore=1.4, spaceAfter=0.6),
        "title": ParagraphStyle("title", parent=body, fontName=BOLD, fontSize=10.6,
                                leading=13, spaceBefore=1.5, spaceAfter=0),
        "meta": ParagraphStyle("meta", parent=body, fontSize=7.8, leading=10.5,
                               textColor=MUTED, spaceBefore=1, spaceAfter=1.5),
        "early": ParagraphStyle("early", parent=body, spaceBefore=3, spaceAfter=1),
        "side": side,
        "caption": ParagraphStyle("caption", parent=side, fontSize=7.6, leading=9.6,
                                  textColor=MUTED, spaceAfter=0),
    }


def heading(text, before=10):
    return Label(text, 8.6, ACCENT, before=before, after=6, rule=True)


def sublabel(text):
    return Label(text, 6.9, MUTED, before=4, after=2.5)


def main_story(cv, st):
    story = [NextPageTemplate("later")]
    lead = [heading("Experience", before=0)]     # stays with the first job
    muted = MUTED.hexval().replace("0x", "#")
    for job in (j for j in cv["jobs"] if not j["early"]):
        part = lead + [Label(job["company"], 7.9, ACCENT, before=0 if lead else 9),
                       Paragraph(job["title"], st["title"]),
                       Paragraph(job["meta"].replace(" · ", "&nbsp;&nbsp;|&nbsp;&nbsp;"), st["meta"])]
        lead = []
        for kind, text in job["blocks"]:
            part.append(Paragraph(text, st[kind], bulletText="•" if kind == "li" else None))
        story.append(KeepTogether(part))
    early = [heading("Earlier experience", before=11)]
    for job in (j for j in cv["jobs"] if j["early"]):
        text = " ".join(t for _, t in job["blocks"])
        early.append(Paragraph(
            f'<b>{job["title"]} · {job["company"]}</b> '
            f'<font color="{muted}">({job["meta"]})</font> {text}', st["early"]))
    story += [KeepTogether(early[:2])] + early[2:]
    return story


def side_first(cv, st):
    flow = [heading("Profile", before=0), Paragraph(cv["profile"], st["side"]),
            heading("Highlights")]
    for label, text in cv["highlights"]:
        flow += [sublabel(label), Paragraph(text, st["side"])]
    flow.append(heading("Languages"))
    for name, level in cv["languages"]:
        flow += [sublabel(name), Paragraph(level[0].upper() + level[1:], st["side"])]
    flow += [heading("Contact"), Paragraph(cv["location"], st["side"])]
    for href, text in cv["links"]:
        text = text.replace("/in/", "/in/<br/>")     # too long for one sidebar line
        flow.append(Paragraph(f'<a href="{href}">{text}</a>', st["side"]))
    return flow


def side_later(cv, st):
    flow = [heading("Selected impact", before=0)]
    for i, (value, caption) in enumerate(cv["impact"]):
        flow.append(Figure(value, caption[0], st["caption"], rule=i < len(cv["impact"]) - 1))
    flow.append(heading("Skills", before=6))
    for label, text in cv["skills"]:
        flow += [sublabel(label), Paragraph(text, st["side"])]
    flow += [heading("Education"),
             Paragraph(f'{cv["school"]}<br/>{cv["degree"]} · {cv["years"]}', st["side"])]
    return flow


def draw_side(canvas, flow, top):
    """Shaded panel sized to its content, with the flowables inside."""
    x, width = MARGIN_X + SIDE_PAD, SIDE_W - 2 * SIDE_PAD
    height, after = 0, None
    for f in flow:      # a frame overlaps the space after one flowable with the next one's space before
        before = 0 if after is None else max(f.getSpaceBefore() - after, 0)
        after = f.getSpaceAfter()
        height += before + f.wrap(width, H)[1] + after
    height -= after
    if height + 2 * SIDE_PAD > top - FOOT:
        sys.exit(f"sidebar does not fit: {height + 2 * SIDE_PAD:.0f} of {top - FOOT:.0f} points")
    canvas.setFillColor(PANEL)
    canvas.roundRect(MARGIN_X, top - height - 2 * SIDE_PAD - 2, SIDE_W,
                     height + 2 * SIDE_PAD + 2, 9, stroke=0, fill=1)
    frame = Frame(x, FOOT - 20, width, top - SIDE_PAD - FOOT + 20, leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)
    frame.addFromList(flow, canvas)
    assert not flow, "sidebar overflow"


def draw_footer(canvas, cv, page):
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.8)
    canvas.line(MARGIN_X, 30, W - MARGIN_X, 30)
    canvas.setFont(REG, 7.4)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 18, "   ·   ".join(text for _, text in reversed(cv["links"])))
    canvas.drawRightString(W - MARGIN_X, 18, str(page))


def first_page(cv, st):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BAND)
        canvas.rect(0, H - BAND_1, W, BAND_1, stroke=0, fill=1)
        canvas.setFillColor(HexColor("#ffffff"))
        canvas.setFont(BOLD, 27)
        canvas.drawString(MARGIN_X, H - 56, cv["name"])
        canvas.setFillColor(ON_BAND)
        canvas.setFont(REG, 12.2)
        canvas.drawString(MARGIN_X, H - 80, "   |   ".join(cv["headline"]))
        canvas.setFillColor(ON_BAND_MUTED)
        canvas.setFont(REG, 9)
        canvas.drawString(MARGIN_X, H - 99, cv["subline"].replace(" · ", "   ·   "))
        col = (W - 2 * MARGIN_X) / len(cv["metrics"])
        for i, (value, caption) in enumerate(cv["metrics"]):
            x = MARGIN_X + i * col
            if i:
                canvas.setStrokeColor(BAND_LINE)
                canvas.setLineWidth(0.7)
                canvas.line(x, H - BAND_1 + 9, x, H - BAND_1 + 42)
                x += 9
            canvas.setFillColor(HexColor("#ffffff"))
            canvas.setFont(BOLD, 14)
            canvas.drawString(x, H - BAND_1 + 31, value)
            canvas.setFillColor(ON_BAND_MUTED)
            canvas.setFont(REG, 6.9)
            for n, line in enumerate(caption):
                canvas.drawString(x, H - BAND_1 + 19 - 8.4 * n, line.replace("&amp;", "&"))
        draw_side(canvas, side_first(cv, st), H - BAND_1 - GAP_TOP)
        draw_footer(canvas, cv, 1)
        canvas.restoreState()
    return draw


def later_page(cv, st):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BAND)
        canvas.rect(0, H - BAND_2, W, BAND_2, stroke=0, fill=1)
        canvas.setFillColor(HexColor("#ffffff"))
        canvas.setFont(BOLD, 11.5)
        canvas.drawString(MARGIN_X, H - 26, cv["name"])
        canvas.setFillColor(ON_BAND)
        canvas.setFont(REG, 8.2)
        canvas.drawRightString(W - MARGIN_X, H - 25.5, "  ·  ".join(cv["headline"][:2]))
        draw_side(canvas, side_later(cv, st), H - BAND_2 - GAP_TOP)
        draw_footer(canvas, cv, doc.page)
        canvas.restoreState()
    return draw


def build():
    fonts()
    st = styles()
    cv = read()

    def frame(band):
        return Frame(MAIN_X, FOOT, MAIN_W, H - band - GAP_TOP - FOOT, leftPadding=0,
                     rightPadding=0, topPadding=0, bottomPadding=0)

    doc = BaseDocTemplate(str(OUT), pagesize=A4, title=f'{cv["name"]} CV', author=cv["name"])
    doc.addPageTemplates([
        PageTemplate("first", [frame(BAND_1)], onPage=first_page(cv, st)),
        PageTemplate("later", [frame(BAND_2)], onPage=later_page(cv, st)),
    ])
    doc.build(main_story(cv, st))
    return doc.page


if __name__ == "__main__":
    pages = build()
    print(f"{OUT.name}: {pages} pages")
    sys.exit(0 if pages == 2 else 1)
