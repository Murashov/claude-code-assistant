"""Build the 2-page PDF CV from cv-2page.html.

Usage (reportlab is not installed system-wide, so use a venv):
    python3 -m venv /path/to/venv && /path/to/venv/bin/pip install reportlab
    /path/to/venv/bin/python work/cv/build_pdf.py

Reads work/cv/cv-2page.html, writes work/cv/Artyom-Murashov-CV.pdf.
Notes marked class="todo" in the HTML are left out of the PDF.
"""
import sys
from html.parser import HTMLParser
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, KeepTogether, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = Path(__file__).parent
SRC = HERE / "cv-2page.html"
OUT = HERE / "Artyom-Murashov-CV.pdf"

INK, MUTED, LINE, ACCENT = (HexColor(c) for c in
                            ("#1c2128", "#5b6472", "#d5dbe3", "#1f4e79"))
SIZE, LEAD = 10, 13              # body font size and leading, in points
MARGIN_X, MARGIN_Y = 15 * mm, 13 * mm
PAD = 6                         # reportlab frames add this padding on every side

BLOCKS = {"h1", "h2", "p", "li"}
DIV_BLOCKS = {"headline", "contact", "job-head"}


class Reader(HTMLParser):
    """Turns the CV page into a flat list of (kind, inline markup) blocks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.kind, self.buf = [], None, []
        self.skip = 0           # depth inside a span.todo
        self.spans = []         # open span classes
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag == "div" and cls == "page":
            self.in_body = True
        if not self.in_body:
            return
        if tag == "section":
            self.blocks.append(("job-start", ""))
        elif tag in BLOCKS or (tag == "div" and cls in DIV_BLOCKS):
            self.kind, self.buf = (cls if tag == "div" else tag), []
        elif tag == "span":
            self.spans.append(cls)
            if cls == "todo":
                self.skip += 1
            elif cls == "meta":
                self.buf.append("\x00")     # splits role from meta
        elif self.kind and not self.skip:
            if tag in ("strong", "b"):
                self.buf.append("<b>")
            elif tag == "a":
                self.buf.append('<a href="%s">' % dict(attrs)["href"])

    def handle_endtag(self, tag):
        if not self.in_body:
            return
        if tag == "span":
            if self.spans and self.spans.pop() == "todo":
                self.skip -= 1
        elif tag == "section":
            self.blocks.append(("job-end", ""))
        elif self.kind and tag in BLOCKS | {"div"}:
            self.blocks.append((self.kind, " ".join("".join(self.buf).split())))
            self.kind = None
        elif self.kind and not self.skip:
            if tag in ("strong", "b"):
                self.buf.append("</b>")
            elif tag == "a":
                self.buf.append("</a>")

    def handle_data(self, data):
        if self.kind and not self.skip:
            text = " ".join(data.split())      # collapse runs, keep edge spaces
            if data[:1].isspace():
                text = " " + text
            if data[-1:].isspace() and text.strip():
                text += " "
            self.buf.append(text.replace("&", "&amp;").replace("<", "&lt;"))


def fonts():
    for name in ("SourceSans3-Regular", "SourceSans3-SemiBold",
                 "SourceSans3-Bold", "SourceSans3-Italic",
                 "SourceSerif4-SemiBold"):
        pdfmetrics.registerFont(TTFont(name, str(HERE / "fonts" / f"{name}.ttf")))
    pdfmetrics.registerFontFamily(
        "SourceSans3-Regular", normal="SourceSans3-Regular",
        bold="SourceSans3-Bold", italic="SourceSans3-Italic",
        boldItalic="SourceSans3-Bold")


def styles():
    base = ParagraphStyle("body", fontName="SourceSans3-Regular", fontSize=SIZE,
                          leading=LEAD, textColor=INK, spaceBefore=1.2, spaceAfter=1.2)
    return {
        "p": base,
        "li": ParagraphStyle("li", parent=base, leftIndent=10, bulletIndent=1.5,
                             spaceBefore=0.8, spaceAfter=0.8),
        "h1": ParagraphStyle("h1", fontName="SourceSerif4-SemiBold", fontSize=21,
                             leading=24, textColor=INK),
        "headline": ParagraphStyle("headline", parent=base, textColor=ACCENT,
                                   fontName="SourceSans3-SemiBold", fontSize=SIZE + 0.4),
        "contact": ParagraphStyle("contact", parent=base, textColor=MUTED,
                                  fontSize=SIZE - 0.8),
        "h2": ParagraphStyle("h2", fontName="SourceSans3-Bold", fontSize=SIZE - 0.4,
                             leading=LEAD, textColor=ACCENT, spaceBefore=7, spaceAfter=1.5),
        "role": ParagraphStyle("role", parent=base, fontName="SourceSans3-Bold",
                               spaceBefore=0, spaceAfter=0),
        "meta": ParagraphStyle("meta", parent=base, textColor=MUTED, alignment=TA_RIGHT,
                               fontSize=SIZE - 0.8, spaceBefore=0, spaceAfter=0),
    }


def job_head(text, st, width):
    role, _, meta = text.partition("\x00")
    meta_w = pdfmetrics.stringWidth(meta.strip(), "SourceSans3-Regular", SIZE - 0.8) + 4
    t = Table([[Paragraph(role.strip(), st["role"]), Paragraph(meta.strip(), st["meta"])]],
              colWidths=[width - meta_w, meta_w])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                           ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    return t


def build():
    fonts()
    st = styles()
    reader = Reader()
    reader.feed(SRC.read_text(encoding="utf-8"))
    width = A4[0] - 2 * MARGIN_X
    story, job = [], None           # job: flowables of the open job, kept on one page
    for kind, text in reader.blocks:
        if kind == "job-start":
            job = [Spacer(1, 5)]
            continue
        if kind == "job-end":
            story.append(KeepTogether(job))
            job = None
            continue
        if kind == "job-head":
            (job if job is not None else story).append(job_head(text, st, width))
            continue
        if kind == "h2":
            flow = [Paragraph(text.upper().replace("&AMP;", "&amp;"), st["h2"]),
                    HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=3)]
        elif kind == "li":
            flow = [Paragraph(text, st["li"], bulletText="•")]
        else:
            flow = [Paragraph(text, st[kind])]
        (job if job is not None else story).extend(flow)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN_X - PAD,
                            rightMargin=MARGIN_X - PAD, topMargin=MARGIN_Y - PAD,
                            bottomMargin=MARGIN_Y - PAD,
                            title="Artyom Murashov CV", author="Artyom Murashov")
    doc.build(story)
    return doc.page


if __name__ == "__main__":
    pages = build()
    print(f"{OUT.name}: {pages} pages")
    sys.exit(0 if pages == 2 else 1)
