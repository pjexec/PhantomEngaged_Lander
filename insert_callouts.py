#!/usr/bin/env python3
"""
Insert Approach A and C callout pages into the ORIGINAL v4 PDF.
No existing pages are modified — only new pages are inserted.

Usage:
  python3 insert_callouts.py "https://your-tool-url.com"
"""

import sys, os
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Flowable
)
from io import BytesIO

# ── Config ──────────────────────────────────────────────────
TOOL_URL   = sys.argv[1] if len(sys.argv) > 1 else "https://expert.email/classify"
ORIG_PDF   = os.path.join(os.path.dirname(os.path.abspath(__file__)),
             "mnt/PhantomEngaged_Lander/Phantom_Engaged_v4.pdf")
OUTPUT     = os.path.join(os.path.dirname(os.path.abspath(__file__)),
             "mnt/PhantomEngaged_Lander/Phantom_Engaged_v5.pdf")
VERSION    = "4.0"      # match original footer
DATE       = "February 2026"

# If running from the workspace folder directly
if not os.path.exists(ORIG_PDF):
    ORIG_PDF = "Phantom_Engaged_v4.pdf"
    OUTPUT   = "Phantom_Engaged_v5.pdf"

W, H = letter

# ── Colours (matched to v4) ─────────────────────────────────
TEAL       = HexColor("#3B9B8F")
DARK_TEXT   = HexColor("#2C3E50")
MID_TEXT    = HexColor("#556677")
LIGHT_TEXT  = HexColor("#8899A6")
CALLOUT_BG  = HexColor("#F0F5F5")
LINK_COLOR  = HexColor("#3B9B8F")

# ── Styles (matched to v4) ──────────────────────────────────
sCalloutNormal = ParagraphStyle(
    "sCalloutNormal", fontName="Helvetica", fontSize=10.5,
    leading=15, textColor=DARK_TEXT, alignment=TA_LEFT,
)
sLinkStyle = ParagraphStyle(
    "sLink", fontName="Helvetica-Bold", fontSize=10.5,
    leading=15, textColor=LINK_COLOR, spaceBefore=4,
)
sH2 = ParagraphStyle(
    "sH2", fontName="Helvetica-Bold", fontSize=14, leading=18,
    textColor=DARK_TEXT, spaceAfter=6, spaceBefore=0,
)
sBody = ParagraphStyle(
    "sBody", fontName="Helvetica", fontSize=10.5, leading=15,
    textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=8,
)


# ── Custom Flowables ────────────────────────────────────────
class TealRule(Flowable):
    def __init__(self, width):
        Flowable.__init__(self)
        self.width = width
        self.height = 4
    def draw(self):
        self.canv.setStrokeColor(TEAL)
        self.canv.setLineWidth(2.5)
        self.canv.line(0, 0, self.width, 0)


class CalloutBox(Flowable):
    """Teal left-border callout box matching v4 styling."""
    def __init__(self, paragraphs_data, avail_width, padding=14):
        Flowable.__init__(self)
        self.bg = CALLOUT_BG
        self.border_color = TEAL
        self.padding = padding
        self.bar_w = 4
        self.avail_width = avail_width
        self.paras = []
        for item in paragraphs_data:
            if isinstance(item, tuple):
                self.paras.append(Paragraph(item[0], item[1]))
            else:
                self.paras.append(Paragraph(item, sCalloutNormal))
        inner_w = avail_width - self.bar_w - self.padding * 2
        self.inner_w = inner_w
        total_h = 0
        for p in self.paras:
            _, ph = p.wrap(inner_w, 10000)
            total_h += ph + 4
        self.box_h = total_h + self.padding * 2 - 4
        self.width = avail_width
        self.height = self.box_h + 8

    def draw(self):
        c = self.canv
        y_base = 4
        c.setFillColor(self.bg)
        c.roundRect(0, y_base, self.avail_width, self.box_h, 2, fill=1, stroke=0)
        c.setFillColor(self.border_color)
        c.rect(0, y_base, self.bar_w, self.box_h, fill=1, stroke=0)
        x = self.bar_w + self.padding
        y = y_base + self.box_h - self.padding
        for p in self.paras:
            _, ph = p.wrap(self.inner_w, 10000)
            p.drawOn(c, x, y - ph)
            y -= ph + 4


# ── Footer matching v4 ──────────────────────────────────────
def draw_footer(canvas, doc, page_num):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(LIGHT_TEXT)
    canvas.drawString(
        inch * 0.85, inch * 0.5,
        f"Phantom Engaged  \u2022  Position Paper v{VERSION}  \u2022  {DATE}   Page {page_num}"
    )
    canvas.drawRightString(
        W - inch * 0.85, inch * 0.5,
        "Chuck Mullaney \u2022 Expert.Email"
    )
    canvas.setStrokeColor(HexColor("#D8DFE3"))
    canvas.setLineWidth(0.4)
    canvas.line(inch * 0.85, inch * 0.65, W - inch * 0.85, inch * 0.65)
    canvas.restoreState()


# ── Build a single-page PDF with callout content ────────────
def make_callout_page(story_items, page_num):
    buf = BytesIO()
    margin = inch * 0.85

    class OnePage(BaseDocTemplate):
        def __init__(self, fh):
            BaseDocTemplate.__init__(self, fh, pagesize=letter,
                leftMargin=margin, rightMargin=margin,
                topMargin=inch * 0.75, bottomMargin=inch * 0.85)
            frame = Frame(margin, inch * 0.85, W - margin*2, H - inch*1.6,
                          id='main')
            self.addPageTemplates([
                PageTemplate(id='callout', frames=frame,
                             onPage=lambda c, d: draw_footer(c, d, page_num))
            ])

    doc = OnePage(buf)
    doc.build(story_items)
    buf.seek(0)
    return buf


# ── Create Approach A page ──────────────────────────────────
def create_approach_a(avail_w):
    """Callout page inserted after the A/B/C framework (after original page 4)."""
    story = [Spacer(1, 20)]

    texts = [
        (f'<b>Apply this framework to your list.</b>  We built a '
         f'<a href="{TOOL_URL}" color="{LINK_COLOR.hexval()}">free classification tool</a> '
         f'to help you map your subscribers into the A/B/C framework described above. There is no opt-in '
         f'and no paywall\u200a\u2014\u200ajust a practical starting point for teams ready to move from '
         f'open-based assumptions to intent-based classification.',
         sCalloutNormal),
    ]
    story.append(CalloutBox(texts, avail_w))
    return story


# ── Create Approach C page ──────────────────────────────────
def create_approach_c(avail_w):
    """Callout page inserted between References and About the Author."""
    story = [Spacer(1, 12)]
    story.append(TealRule(avail_w))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Put This Into Practice", sH2))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The ideas in this paper become useful when you apply them to your own subscriber data. "
        "To make that starting point easier, we built a free tool that walks you through the A/B/C "
        "classification framework described in Section 4.",
        sBody
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f'There is no opt-in, no paywall, and no sales pitch. It exists to help working marketers '
        f'put classification discipline into practice.  '
        f'<a href="{TOOL_URL}" color="{LINK_COLOR.hexval()}">Access the free tool here.</a>',
        sBody
    ))
    return story


# ── Main assembly ───────────────────────────────────────────
def build():
    reader = PdfReader(ORIG_PDF)
    writer = PdfWriter()
    avail_w = W - inch * 1.7

    # Original has 9 pages (cover=0, content=1-8)
    # Insert A after page index 3 (original page 4 = "Classification Framework")
    # Insert C after page index 7 (original page 8 = "Conclusion + References")
    # then page index 8 (About the Author) follows

    # Build the two callout pages
    # For page numbering: A goes after original page 4 (which shows "Page 3")
    # so the new A page would logically be ~page 4 area
    a_story = create_approach_a(avail_w)
    a_buf = make_callout_page(a_story, page_num=3)  # sits between page 3 and 4 content
    a_reader = PdfReader(a_buf)

    c_story = create_approach_c(avail_w)
    c_buf = make_callout_page(c_story, page_num=8)  # sits after page 7 content
    c_reader = PdfReader(c_buf)

    # Assemble
    for i in range(len(reader.pages)):
        writer.add_page(reader.pages[i])

        # After page 4 (index 3), insert Approach A
        if i == 3:
            writer.add_page(a_reader.pages[0])

        # After page 8 (index 7), insert Approach C
        if i == 7:
            writer.add_page(c_reader.pages[0])

    with open(OUTPUT, "wb") as f:
        writer.write(f)

    print(f"\n  Generated: {OUTPUT}")
    print(f"  URL: {TOOL_URL}")
    print(f"  Original pages preserved. Two callout pages inserted.\n")

if __name__ == "__main__":
    build()
