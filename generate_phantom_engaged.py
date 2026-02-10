#!/usr/bin/env python3
"""
Phantom Engaged Position Paper Generator
=========================================

Generates a complete Phantom Engaged v5 PDF with partner-specific
tracking links baked into two callout placements.

USAGE:
  python3 generate_phantom_engaged.py                         # default link
  python3 generate_phantom_engaged.py "https://partner.link"  # custom link

The same URL is used in both the Approach-A callout (after the A/B/C
framework) and the Approach-C "Put This Into Practice" section (before
References).  Change it per partner — everything else stays identical.
"""

import sys
import os

# ============================================================
# CONFIGURATION — change the default URL here if you like
# ============================================================
TOOL_URL = sys.argv[1] if len(sys.argv) > 1 else "https://expert.email/classify"
VERSION  = "4.0"
DATE     = "February 2026"
OUTPUT   = "Phantom_Engaged_v5.pdf"

# ============================================================
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, Flowable, KeepTogether, NextPageTemplate
)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# ── Colour palette (matched to v4) ────────────────────────────
COVER_BG    = HexColor("#2D3E4D")
TEAL        = HexColor("#3B9B8F")
DARK_TEXT    = HexColor("#2C3E50")
MID_TEXT     = HexColor("#556677")
LIGHT_TEXT   = HexColor("#8899A6")
CALLOUT_BG   = HexColor("#F0F5F5")
TABLE_HDR    = HexColor("#2D3E4D")
TABLE_ALT    = HexColor("#F7FAFA")
LINK_COLOR   = HexColor("#3B9B8F")

W, H = letter  # 612 x 792

# ── Paragraph styles ──────────────────────────────────────────
sNormal = ParagraphStyle(
    "sNormal", fontName="Helvetica", fontSize=10.5, leading=15,
    textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=8,
)
sBold = ParagraphStyle(
    "sBold", parent=sNormal, fontName="Helvetica-Bold",
)
sItalic = ParagraphStyle(
    "sItalic", parent=sNormal, fontName="Helvetica-Oblique",
    fontSize=10.5, leading=15, textColor=MID_TEXT,
)
sH1 = ParagraphStyle(
    "sH1", fontName="Helvetica-Bold", fontSize=22, leading=27,
    textColor=DARK_TEXT, spaceAfter=4, spaceBefore=18,
)
sH2 = ParagraphStyle(
    "sH2", fontName="Helvetica-Bold", fontSize=14, leading=18,
    textColor=DARK_TEXT, spaceAfter=6, spaceBefore=14,
)
sH3 = ParagraphStyle(
    "sH3", fontName="Helvetica-Bold", fontSize=12, leading=16,
    textColor=TEAL, spaceAfter=4, spaceBefore=10,
)
sBullet = ParagraphStyle(
    "sBullet", parent=sNormal, leftIndent=20, bulletIndent=8,
    spaceBefore=4, spaceAfter=4,
)
sRef = ParagraphStyle(
    "sRef", fontName="Helvetica", fontSize=8.5, leading=12,
    textColor=MID_TEXT, spaceAfter=3,
)
sFooter = ParagraphStyle(
    "sFooter", fontName="Helvetica", fontSize=8, leading=10,
    textColor=LIGHT_TEXT,
)
sCalloutItalic = ParagraphStyle(
    "sCalloutItalic", fontName="Helvetica-Oblique", fontSize=10.5,
    leading=15, textColor=MID_TEXT, alignment=TA_LEFT,
)
sCalloutNormal = ParagraphStyle(
    "sCalloutNormal", fontName="Helvetica", fontSize=10.5,
    leading=15, textColor=DARK_TEXT, alignment=TA_LEFT,
)
sTableCell = ParagraphStyle(
    "sTableCell", fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK_TEXT, alignment=TA_LEFT,
)
sTableHdr = ParagraphStyle(
    "sTableHdr", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    textColor=white, alignment=TA_LEFT,
)
sTableBoldCell = ParagraphStyle(
    "sTableBoldCell", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    textColor=DARK_TEXT, alignment=TA_LEFT,
)
sLinkStyle = ParagraphStyle(
    "sLink", parent=sCalloutNormal, fontName="Helvetica-Bold",
    fontSize=10.5, textColor=LINK_COLOR, spaceBefore=4,
)


# ── Custom flowables ──────────────────────────────────────────
class TealRule(Flowable):
    """Horizontal teal line under section headers."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.width = width
        self.height = 4
    def draw(self):
        self.canv.setStrokeColor(TEAL)
        self.canv.setLineWidth(2.5)
        self.canv.line(0, 0, self.width, 0)


class CalloutBox(Flowable):
    """Teal left-border callout with light background."""
    def __init__(self, text_paragraphs, avail_width, bg=CALLOUT_BG,
                 border_color=TEAL, padding=14, style=None):
        Flowable.__init__(self)
        self.bg = bg
        self.border_color = border_color
        self.padding = padding
        self.bar_w = 4
        self.avail_width = avail_width
        if style is None:
            style = sCalloutItalic
        self.paras = []
        for t in text_paragraphs:
            if isinstance(t, tuple):
                self.paras.append(Paragraph(t[0], t[1]))
            else:
                self.paras.append(Paragraph(t, style))
        inner_w = avail_width - self.bar_w - self.padding * 2
        self.inner_w = inner_w
        total_h = 0
        for para in self.paras:
            _, ph = para.wrap(inner_w, 10000)
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
        for para in self.paras:
            _, ph = para.wrap(self.inner_w, 10000)
            para.drawOn(c, x, y - ph)
            y -= ph + 4


class OverlapDiagram(Flowable):
    """The Phantom Engaged overlap visualization — matched to v4.

    Uses reportlab.graphics Drawing/shapes for reliable fill rendering.
    """
    def __init__(self, avail_width):
        Flowable.__init__(self)
        self.width = avail_width
        self.height = 120

    def draw(self):
        W = self.width
        H = self.height
        d = Drawing(W, H)

        cx = W / 2
        box_w = W * 0.82
        box_h = 38
        box_x = cx - box_w / 2
        box_y = 28
        r = 4
        dash_x = box_x + box_w * 0.72
        lw = 1.2

        # Layer 1: Full teal-filled rounded rect (whole box)
        d.add(Rect(box_x, box_y, box_w, box_h, rx=r, ry=r,
                   fillColor=HexColor("#D0EDEA"),
                   strokeColor=None, strokeWidth=0))

        # Layer 2: White rect over the right portion (dash_x to right edge)
        d.add(Rect(dash_x, box_y + lw/2,
                   (box_x + box_w - r) - dash_x, box_h - lw,
                   fillColor=white, strokeColor=None, strokeWidth=0))

        # Layer 3: Teal border (stroke only, no fill)
        d.add(Rect(box_x, box_y, box_w, box_h, rx=r, ry=r,
                   fillColor=None,
                   strokeColor=TEAL, strokeWidth=lw))

        # Dashed vertical boundary line
        d.add(Line(dash_x, box_y, dash_x, box_y + box_h,
                   strokeColor=LIGHT_TEXT, strokeWidth=1,
                   strokeDashArray=[4, 3]))

        # "ENGAGED" label (left inside box)
        d.add(String(box_x + 20, box_y + box_h/2 - 3, "ENGAGED",
                     fontName="Helvetica-Bold", fontSize=10,
                     fillColor=DARK_TEXT))

        # "UNENGAGED" label (right inside box)
        d.add(String(box_x + box_w - 20, box_y + box_h/2 - 3, "UNENGAGED",
                     fontName="Helvetica-Bold", fontSize=10,
                     fillColor=DARK_TEXT, textAnchor="end"))

        # "PHANTOM ENGAGED" label above
        d.add(String(cx, box_y + box_h + 18, "PHANTOM ENGAGED",
                     fontName="Helvetica-Bold", fontSize=9,
                     fillColor=TEAL, textAnchor="middle"))

        # Arrow line down to box
        d.add(Line(cx, box_y + box_h + 16, cx, box_y + box_h + 2,
                   strokeColor=DARK_TEXT, strokeWidth=0.8))

        # Subtitle lines below diagram
        d.add(String(cx, box_y - 8, "Looks engaged in reports,",
                     fontName="Helvetica", fontSize=8,
                     fillColor=LIGHT_TEXT, textAnchor="middle"))
        d.add(String(cx, box_y - 18, "but attention is uncertain",
                     fontName="Helvetica", fontSize=8,
                     fillColor=LIGHT_TEXT, textAnchor="middle"))
        d.add(String(cx, box_y - 32,
                     "Privacy protections increase the overlap between what we can measure and what is real.",
                     fontName="Helvetica-Oblique", fontSize=7.5,
                     fillColor=MID_TEXT, textAnchor="middle"))

        # Render the Drawing onto the canvas
        renderPDF.draw(d, self.canv, 0, 0)


# ── Page templates ────────────────────────────────────────────
class CoverPage:
    """Draw full-bleed dark cover matching v4."""
    @staticmethod
    def draw(canvas, doc):
        canvas.saveState()
        # Dark background
        canvas.setFillColor(COVER_BG)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # Teal left accent bar — alongside title/author block only
        bar_x = inch * 0.95
        bar_bottom = H - inch * 5.05   # just below version/date line
        bar_height = (H - inch * 1.5) - bar_bottom  # extends above title
        canvas.setFillColor(TEAL)
        canvas.rect(bar_x, bar_bottom, 4, bar_height, fill=1, stroke=0)
        # Title
        canvas.setFont("Helvetica-Bold", 58)
        canvas.setFillColor(white)
        canvas.drawString(inch * 1.15, H - inch * 1.8, "Phantom")
        canvas.drawString(inch * 1.15, H - inch * 2.55, "Engaged")
        # Subtitle
        canvas.setFont("Helvetica", 13)
        canvas.setFillColor(HexColor("#8FA8B8"))
        y_sub = H - inch * 3.1
        canvas.drawString(inch * 1.15, y_sub,
            "A position paper on the invisible overlap between engaged")
        canvas.drawString(inch * 1.15, y_sub - 17,
            "and disengaged subscribers created by modern email")
        canvas.drawString(inch * 1.15, y_sub - 34, "privacy protections")
        # Horizontal rule
        canvas.setStrokeColor(HexColor("#4A6070"))
        canvas.setLineWidth(0.5)
        canvas.line(inch * 1.15, y_sub - 52, W - inch * 1.0, y_sub - 52)
        # Author info
        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(TEAL)
        canvas.drawString(inch * 1.15, y_sub - 75, "Chuck Mullaney")
        canvas.setFont("Helvetica", 11)
        canvas.setFillColor(LIGHT_TEXT)
        canvas.drawString(inch * 1.15, y_sub - 93, "Expert.Email")
        canvas.drawString(inch * 1.15, y_sub - 111,
            f"Version {VERSION}  \u2022  {DATE}")

        # Bottom callout box
        bx = inch * 1.15
        by = inch * 1.3
        bw = W - inch * 2.15
        bh = inch * 0.95
        canvas.setFillColor(HexColor("#253545"))
        canvas.roundRect(bx, by, bw, bh, 3, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(bx, by, 4, bh, fill=1, stroke=0)
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.setFillColor(HexColor("#B0C4CE"))
        txt1 = "When privacy protections break open tracking, a large portion of your list becomes impossible to classify using"
        txt2 = "email analytics alone. That invisible overlap is the Phantom Engaged problem: people who look engaged in"
        txt3 = "reports but may or may not be paying attention."
        canvas.drawString(bx + 18, by + bh - 24, txt1)
        canvas.drawString(bx + 18, by + bh - 39, txt2)
        canvas.drawString(bx + 18, by + bh - 54, txt3)

        # Copyright
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(HexColor("#607080"))
        canvas.drawString(inch * 1.15, inch * 0.75,
            "\u00A9 2026 Chuck Mullaney. You may share this document in full with attribution.")
        canvas.restoreState()


class ContentPage:
    """Footer on content pages — matches v4 layout."""
    @staticmethod
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(LIGHT_TEXT)
        canvas.drawString(
            inch * 0.85, inch * 0.5,
            f"Phantom Engaged  \u2022  Position Paper v{VERSION}  \u2022  {DATE}   Page {doc.page - 1}"
        )
        canvas.drawRightString(
            W - inch * 0.85, inch * 0.5,
            "Chuck Mullaney \u2022 Expert.Email"
        )
        canvas.setStrokeColor(HexColor("#D8DFE3"))
        canvas.setLineWidth(0.4)
        canvas.line(inch * 0.85, inch * 0.65, W - inch * 0.85, inch * 0.65)
        canvas.restoreState()


# ── Helpers ────────────────────────────────────────────────────
def sec(title):
    return [Paragraph(title, sH1), TealRule(W - inch * 1.7), Spacer(1, 8)]

def subsec(title):
    return [Paragraph(title, sH2), Spacer(1, 4)]

def h3(title):
    """Teal bold subsection header (used in Section 8)."""
    return [Paragraph(title, sH3), Spacer(1, 4)]

def p(text, style=sNormal):
    return Paragraph(text, style)

def sp(h=6):
    return Spacer(1, h)

def callout(texts, avail_w, style=None, bg=CALLOUT_BG):
    return CalloutBox(texts, avail_w, bg=bg, style=style)

def bullet(text):
    return Paragraph(f"\u2022  {text}", sBullet)


# ── Build document ────────────────────────────────────────────
def build():
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT)
    margin = inch * 0.85
    avail_w = W - margin * 2
    story = []

    # ── Cover page placeholder ──
    story.append(Spacer(1, H))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════
    story.extend(sec("Executive Summary"))

    story.append(p(
        "For years, marketers treated opens as a proxy for attention. That proxy is now unreliable at scale."
    ))
    story.append(sp())

    story.append(p(
        "Apple Mail Privacy Protection (MPP) is designed to prevent senders from learning about Mail activity by "
        "downloading remote content in the background, not only when someone views the message, and by "
        "obscuring IP-based inference. <super>[1][2]</super>"
    ))
    story.append(sp())

    story.append(p(
        "This shift creates a practical failure mode: you can no longer confidently distinguish between a quiet, "
        "loyal reader and a truly disengaged recipient whose client triggered tracking anyway. Those two people "
        "collapse into the same reporting bucket when you rely on opens."
    ))
    story.append(sp())

    story.append(p(
        "That collapse goes beyond analytics. It causes real list damage when marketers run re-engagement or "
        "suppression based on signals that no longer map cleanly to human attention. In the post-privacy world, "
        "the highest risk is not the subscribers you can clearly identify as inactive. It is the subscribers who "
        "<i>appear</i> active but whose attention cannot be verified."
    ))
    story.append(sp())

    story.append(callout([
        "Phantom Engaged is the name for that uncertainty bucket: an unavoidable overlap created when privacy "
        "protections break our ability to distinguish silence from disengagement using email metrics alone."
    ], avail_w))
    story.append(sp())

    story.append(p(
        "The practical solution is not a clever new metric. It is a classification stance: use intentional actions as "
        "proof of engagement, treat opens as weak evidence, and handle ambiguity conservatively to avoid "
        "irreversible harm."
    ))

    # ══════════════════════════════════════════════════════════
    # SECTION 1
    # ══════════════════════════════════════════════════════════
    story.extend(sec("1. What Changed in Measurement"))

    story.append(p(
        "The modern inbox is increasingly built to protect recipients from hidden tracking. Apple\u2019s approach is "
        "the most explicit: when a user enables Protect Mail Activity, remote content is privately downloaded in "
        "the background when the email is received, rather than when it is viewed, helping prevent senders from "
        "learning about Mail activity. <super>[1][2]</super>"
    ))
    story.append(sp())

    story.append(p(
        "From a marketer\u2019s perspective, that background fetch is the core issue. The tracking pixel may load even "
        "if the person never intentionally opened the email. Many email platforms now expose indicators for "
        "machine-generated opens or MPP-related opens for this reason (for example, SendGrid\u2019s MPP flag). <super>[3]</super>"
    ))
    story.append(sp())

    story.append(p(
        "At the same time, mailbox providers are tightening sender expectations around authentication, "
        "one-click unsubscribe, and complaint thresholds. <super>[4][5]</super> The ecosystem is simultaneously becoming less "
        "measurable and less forgiving."
    ))
    story.append(sp())

    story.append(callout([
        ("<b>The core tension:</b> <i>You are being asked to prove you send wanted mail while losing the cleanest historical "
         "proxy (opens) that many teams relied on to define \u2018wanted.\u2019</i>", sCalloutNormal)
    ], avail_w))

    # ══════════════════════════════════════════════════════════
    # SECTION 2
    # ══════════════════════════════════════════════════════════
    story.extend(sec("2. Why the Open Event No Longer Means Attention"))

    story.append(p(
        "Opens were always an indirect measurement. Even before MPP, they depended on image loading, client "
        "settings, caching behaviors, security tools, and link-scanning. Privacy protections push this from "
        "\u2018imperfect\u2019 to \u2018structurally unreliable\u2019 for classification purposes."
    ))
    story.append(sp(10))

    # Signal comparison table — fixed column widths to prevent overflow
    tdata = [
        [Paragraph("<b>Signal</b>", sTableHdr),
         Paragraph("<b>Pre-Privacy Implication</b>", sTableHdr),
         Paragraph("<b>Post-Privacy Reality</b>", sTableHdr)],
        [Paragraph("<b>Open</b>", sTableBoldCell),
         Paragraph("A person likely viewed the email.", sTableCell),
         Paragraph("Often means the client fetched images. May happen without a human reading.", sTableCell)],
        [Paragraph("<b>No open</b>", sTableBoldCell),
         Paragraph("A person likely did not view the email.", sTableCell),
         Paragraph("Could be a non-reader, or a reader whose client blocks tracking.", sTableCell)],
        [Paragraph("<b>Click</b>", sTableBoldCell),
         Paragraph("A person intentionally acted.", sTableCell),
         Paragraph("Still the cleanest in-email proof of intent. Not perfect, but far stronger than opens.", sTableCell)],
        [Paragraph("<b>Reply</b>", sTableBoldCell),
         Paragraph("A person intentionally engaged.", sTableCell),
         Paragraph("High-confidence intent signal. May bypass link blockers and tracking limitations.", sTableCell)],
        [Paragraph("<b>Purchase / login</b>", sTableBoldCell),
         Paragraph("Downstream proof of value.", sTableCell),
         Paragraph("Best proof if you can connect it. The gold standard for classification.", sTableCell)],
    ]
    col_w = [avail_w * 0.15, avail_w * 0.35, avail_w * 0.50]
    t = Table(tdata, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HDR),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, 1), TABLE_ALT),
        ('BACKGROUND', (0, 3), (-1, 3), TABLE_ALT),
        ('BACKGROUND', (0, 5), (-1, 5), TABLE_ALT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor("#D8DFE3")),
    ]))
    story.append(t)
    story.append(sp(10))

    story.append(callout([
        "If you take one thing from this paper, take this: opens are now evidence that something rendered remote "
        "content, not evidence that a person noticed, read, agreed, or wanted more."
    ], avail_w))

    # ══════════════════════════════════════════════════════════
    # SECTION 3
    # ══════════════════════════════════════════════════════════
    story.extend(sec("3. The Phantom Engaged Overlap"))

    story.append(p(
        "In a pre-privacy mental model, the list felt cleanly separable: engaged subscribers showed opens and "
        "clicks; disengaged subscribers went dark. In the post-privacy model, measurement pushes a large "
        "number of people into the same middle zone: visible activity without confirmable intent."
    ))
    story.append(sp(8))

    story.append(OverlapDiagram(avail_w))
    story.append(sp(8))

    story.append(p(
        "That overlap is not a new audience segment you can optimize away. It is a fact of measurement "
        "uncertainty. Attempting to force certainty (for example, by treating opens as attention regardless) is "
        "where most classification mistakes begin."
    ))

    # ══════════════════════════════════════════════════════════
    # SECTION 4
    # ══════════════════════════════════════════════════════════
    story.extend(sec("4. A Classification Framework That Admits Uncertainty"))

    story.append(p(
        "Most engagement models assume clean boundaries. The A/B/C framework starts from the opposite "
        "premise: uncertainty is the default state, and the burden of proof falls on the signals, not on the "
        "subscriber. It is intentionally conservative, designed to protect silent readers and prevent irreversible "
        "decisions based on noisy data."
    ))
    story.append(sp(10))

    # A/B/C classification table — fixed column widths
    abc_data = [
        [Paragraph("", sTableHdr),
         Paragraph("<b>Classification</b>", sTableHdr),
         Paragraph("<b>Signals</b>", sTableHdr),
         Paragraph("<b>Treatment</b>", sTableHdr)],
        [Paragraph("<b><font size='16' color='#3B9B8F'>A</font></b>", sTableBoldCell),
         Paragraph("<b>Confirmed Intent</b>", sTableBoldCell),
         Paragraph("Clicks, replies, purchases, logins, downstream events. Opens optional.", sTableCell),
         Paragraph("Send with confidence. These subscribers have demonstrated attention.", sTableCell)],
        [Paragraph("<b><font size='16' color='#3B9B8F'>B</font></b>", sTableBoldCell),
         Paragraph("<b>Phantom (Uncertain)</b>", sTableBoldCell),
         Paragraph("Opens present. No intentional actions. Ambiguous by design.", sTableCell),
         Paragraph("Handle conservatively. This is a holding state, not a verdict.", sTableCell)],
        [Paragraph("<b><font size='16' color='#3B9B8F'>C</font></b>", sTableBoldCell),
         Paragraph("<b>Unengaged (Observable)</b>", sTableBoldCell),
         Paragraph("No opens, clicks, replies, or downstream actions within a defined window.", sTableCell),
         Paragraph("Eligible for controlled, finite re-engagement. Safest to suppress or sunset. Clearest candidates for removal.", sTableCell)],
    ]
    abc_col = [avail_w * 0.06, avail_w * 0.18, avail_w * 0.38, avail_w * 0.38]
    at = Table(abc_data, colWidths=abc_col, repeatRows=1)
    at.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HDR),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, 1), TABLE_ALT),
        ('BACKGROUND', (0, 3), (-1, 3), TABLE_ALT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor("#D8DFE3")),
    ]))
    story.append(at)
    story.append(sp(10))

    story.append(p(
        "<b>An important distinction:</b> Bucket B is not a behavior segment or a personality type. It is a holding state "
        "that says: \u201CWe don\u2019t currently have enough proof to classify this person as engaged or disengaged.\u201D "
        "Treating it as anything else defeats its purpose."
    ))
    story.append(sp(10))

    # ══════════════════════════════════════════════════════════
    # APPROACH A — free tool callout (hidden link)
    # ══════════════════════════════════════════════════════════
    tool_callout_texts = [
        (f'<b>Apply this framework to your list.</b>  We built a '
         f'<a href="{TOOL_URL}" color="{LINK_COLOR.hexval()}">free classification tool</a> '
         f'to help you map your subscribers into the A/B/C framework described above. '
         f'There is no opt-in and no paywall\u200a\u2014\u200ajust a practical starting point for teams '
         f'ready to move from open-based assumptions to intent-based classification.',
         sCalloutNormal),
    ]
    story.append(callout(tool_callout_texts, avail_w))

    # ══════════════════════════════════════════════════════════
    # SECTION 5
    # ══════════════════════════════════════════════════════════
    story.extend(sec("5. What Goes Wrong When You Ignore the Uncertainty"))

    story.append(p(
        "Most list harm in the post-privacy era happens when teams apply pre-privacy rules to post-privacy "
        "signals. These mistakes are common, understandable, and worth naming clearly so you can recognize "
        "them in your own program:"
    ))
    story.append(sp(4))

    story.append(bullet(
        "<b>Resend-to-non-openers becomes a frequency amplifier.</b> What was once a relevance tactic now "
        "adds volume to inboxes that may already be receiving your emails, just without generating a "
        "trackable open."
    ))
    story.append(bullet(
        "<b>Aggressive \u201Clast chance\u201D campaigns pressure silent readers.</b> When quiet loyalty looks identical "
        "to disengagement in your data, urgency-based re-engagement risks pushing away people who "
        "were still paying attention."
    ))
    story.append(bullet(
        "<b>Open-based suppression quietly removes high-value subscribers.</b> Readers whose clients block "
        "tracking or who consume emails without triggering pixels get sorted into your inactive bucket, and "
        "deleted."
    ))
    story.append(bullet(
        "<b>Dashboard confidence replaces relationship awareness.</b> Teams over-trust reporting and "
        "under-trust what they know about long-term customer behavior and brand affinity."
    ))
    story.append(sp(4))

    story.append(p(
        "These errors are rarely visible in the moment because the reporting still looks healthy. The cost shows up "
        "over time: higher complaint rates, weaker inbox placement, reduced conversion, and a list that grows "
        "harder to recover."
    ))
    story.append(sp())

    story.append(callout([
        "Phantom Engaged is why modern re-engagement is primarily a risk management problem. The most "
        "important decisions are about what you choose <b>not</b> to do when you cannot know the full truth from email "
        "metrics alone."
    ], avail_w))

    # ══════════════════════════════════════════════════════════
    # SECTION 6
    # ══════════════════════════════════════════════════════════
    story.extend(sec("6. Principles for Working Marketers"))

    story.append(p(
        "These are principles, not tactics. Tactics change with platforms and tools. Principles hold up regardless "
        "of which ESP you use or how large your list is."
    ))
    story.append(sp(4))

    story.extend(subsec("Principle 1: Intentional proof beats inferred attention."))
    story.append(p(
        "Clicks, replies, purchases, logins, and other downstream events are not perfect, but they reflect "
        "deliberate action. Build your classification around these signals first. Treat opens as supporting "
        "evidence, not as the foundation."
    ))
    story.append(sp(4))

    story.extend(subsec("Principle 2: When you are uncertain, restraint is a strategy."))
    story.append(p(
        "When you cannot safely distinguish a loyal quiet reader from a non-reader, pressure and urgency-based "
        "tactics carry real risk. It is better to reduce frequency, adjust content, or route people into lower-pressure "
        "paths than to gamble trust for short-term clarity."
    ))
    story.append(sp(4))

    story.extend(subsec("Principle 3: Classify first, optimize second."))
    story.append(p(
        "Optimization assumes your labels are correct. In the post-privacy world, those labels are often wrong. "
        "Invest in building a truthful classification stance before chasing marginal KPI lifts. The returns from "
        "accurate classification will outperform the returns from optimizing against flawed segments."
    ))
    story.append(sp(4))

    story.extend(subsec("Principle 4: Lock your observation windows before judging."))
    story.append(p(
        "An observation window is the amount of time you commit to watching for an intentional signal before "
        "changing how you treat someone. Set it in advance. Without a fixed window, it is easy to unconsciously "
        "move the goalposts to match whatever story your dashboard is telling that week. A locked window turns "
        "engagement policy into a fair, repeatable process."
    ))
    story.append(sp(4))

    story.extend(subsec("Principle 5: Prefer reversible actions over irreversible ones."))
    story.append(p(
        "When you are unsure, choose actions you can undo. Reducing frequency, changing content, or moving "
        "people into a different sending cadence are all reversible. Suppression and permanent removal are not. "
        "Save irreversible decisions for situations where you have high confidence."
    ))

    # ══════════════════════════════════════════════════════════
    # SECTION 7
    # ══════════════════════════════════════════════════════════
    story.extend(sec("7. A Note on Ethics and Privacy"))

    story.append(p(
        "Phantom Engaged is not a call to outsmart privacy protections. Those protections exist because "
        "recipients deserve control over how they are tracked. The appropriate response is to adapt how we "
        "interpret metrics and how we treat people, not to find clever workarounds."
    ))
    story.append(sp(2))
    story.append(p("This paper takes a clear stance on where the line should be:"))
    story.append(sp(4))

    story.append(bullet(
        "Deceptive workarounds designed to recreate individual-level surveillance undermine the trust that "
        "makes email marketing sustainable."
    ))
    story.append(bullet(
        "People should not be penalized for failing to produce trackable signals. Silence is not the same as "
        "rejection."
    ))
    story.append(bullet(
        "Manufacturing urgency to force clicks as a \u201Cproof of life\u201D mechanism treats subscribers as problems "
        "to solve rather than people to serve."
    ))
    story.append(bullet(
        "The better path is consent-based: clear expectations, easy unsubscribe, and content that earns "
        "attention on its own merits."
    ))
    story.append(sp(4))

    story.append(p(
        "This stance also aligns with the direction mailbox providers are heading: easier unsubscribe, stronger "
        "authentication requirements, and lower tolerance for unwanted mail. <super>[4][5]</super> Working with that "
        "trajectory, rather than against it, is both the ethical choice and the practical one."
    ))

    # ══════════════════════════════════════════════════════════
    # SECTION 8
    # ══════════════════════════════════════════════════════════
    story.extend(sec("8. What Competent Teams Do Next"))

    story.append(p(
        "This is not a campaign checklist. It is a governance upgrade: changes to the rules your email program "
        "runs on."
    ))
    story.append(sp(4))

    story.extend(h3("Adopt a measurement hierarchy."))
    story.append(p(
        "Write down, in order, which signals you trust most for engagement classification. In most programs, "
        "downstream events and replies outrank clicks, and clicks outrank opens. Having this documented "
        "means your team makes consistent decisions instead of defaulting to whatever metric is easiest to pull."
    ))
    story.append(sp(4))

    story.extend(h3("Separate deliverability safety from performance reporting."))
    story.append(p(
        "Your dashboard is a performance tool. It should not be the final authority on who stays and who goes. "
        "Deliverability safety policies should be conservative by default and should explicitly account for the "
        "uncertainty that privacy-inflated opens create."
    ))
    story.append(sp(4))

    story.extend(h3("Design for silent readers."))
    story.append(p(
        "Accept that a meaningful percentage of your audience will never click but still receives value from your "
        "emails. If your program requires clicking to avoid being treated as inactive, your program is hostile to a "
        "real segment of real people. That is worth examining."
    ))
    story.append(sp(4))

    story.extend(h3("Reduce emotional automation."))
    story.append(p(
        "Revisit any automation that interprets silence as rejection. In the post-privacy world, silence is often just "
        "silence, not a statement about your brand, your content, or your value."
    ))
    story.append(sp(4))

    story.extend(h3("Invest in proof where it actually exists."))
    story.append(p(
        "Where feasible, connect email to outcomes you can verify: purchases, logins, subscription renewals, "
        "product usage. This is not about surveilling individuals. It is about ensuring you are not mistaking a "
        "privacy artifact for actual disengagement."
    ))

    # ══════════════════════════════════════════════════════════
    # CONCLUSION
    # ══════════════════════════════════════════════════════════
    story.extend(sec("Conclusion"))

    story.append(p(
        "Phantom Engaged is the name for a reality email marketers can no longer afford to ignore: a large "
        "portion of your list now sits in an overlap where the most common engagement signal (opens) is not "
        "trustworthy proof of attention."
    ))
    story.append(sp())

    story.append(p(
        "The correct response is not panic, and it is not denial. It is classification discipline: prove intent where "
        "you can, admit uncertainty where you must, and treat that uncertainty with restraint."
    ))
    story.append(sp(8))

    final_callout = [
        ("<b>If you share one sentence with your team, share this:</b>", sCalloutNormal),
        ("<i>Stop asking your dashboards to answer a question they can no longer answer. Replace false certainty with "
         "policies that protect trust and list health.</i>", sCalloutItalic),
    ]
    story.append(callout(final_callout, avail_w))
    story.append(sp(16))

    # ══════════════════════════════════════════════════════════
    # APPROACH C — "Put This Into Practice" (hidden link)
    # ══════════════════════════════════════════════════════════
    story.append(TealRule(avail_w))
    story.append(sp(16))
    story.append(Paragraph("Put This Into Practice", sH2))
    story.append(sp(10))
    story.append(p(
        "The ideas in this paper become useful when you apply them to your own subscriber data. "
        "To make that starting point easier, we built a free tool that walks you through the A/B/C "
        "classification framework described in Section 4."
    ))
    story.append(sp(4))
    story.append(p(
        f'There is no opt-in, no paywall, and no sales pitch. It exists to help working marketers '
        f'put classification discipline into practice.  '
        f'<a href="{TOOL_URL}" color="{LINK_COLOR.hexval()}">Access the free tool here.</a>'
    ))
    story.append(sp(16))

    # ══════════════════════════════════════════════════════════
    # REFERENCES (kept together to prevent orphaned refs)
    # ══════════════════════════════════════════════════════════
    refs_block = [TealRule(avail_w), sp(12)]
    refs_block.append(Paragraph("<b>References</b>", sH2))
    refs_block.append(sp(6))

    refs = [
        '[1] Apple. "Mail Privacy Protection & Privacy." Apple Legal. apple.com/legal/privacy/data/en/mail-privacy-protection/',
        '[2] Apple Support. "Use Mail Privacy Protection on Mac." support.apple.com/guide/mail/use-mail-privacy-protection-mlhl03be2866/mac',
        '[3] Twilio SendGrid Docs. "Understanding Apple Mail Privacy Protection and Open Events" and Event Webhook reference for MPP-generated opens.',
        '[4] Google Workspace Admin Help. "Email sender guidelines" (bulk sender expectations including one-click unsubscribe). support.google.com/a/answer/81126',
        '[5] Yahoo. "Sender Best Practices" (includes one-click unsubscribe guidance and processing expectations). senders.yahooinc.com/best-practices/',
    ]
    for r in refs:
        refs_block.append(Paragraph(r, sRef))

    story.append(KeepTogether(refs_block))

    # ══════════════════════════════════════════════════════════
    # ABOUT THE AUTHOR
    # ══════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(TealRule(avail_w))
    story.append(sp(12))
    story.append(Paragraph("<b>About the Author</b>", sH2))
    story.append(sp(6))

    story.append(p(
        "Chuck Mullaney brings 25 years of digital marketing expertise, with 15 years dedicated exclusively to email "
        "marketing and inbox deliverability. He has architected six email platforms: two public facing systems that "
        "achieved significant market adoption, and four proprietary platforms built for private clients."
    ))
    story.append(sp())
    story.append(p(
        "In his administrative oversight of the two public platforms, Chuck gained unique insight into the email "
        "marketing strategies of 26,000 businesses, observing firsthand their approaches to campaigns, automation, "
        "deliverability challenges, and subscriber engagement. This rare vantage point, combined with years of "
        "consulting for mid market and enterprise clients, has given him comprehensive experience in the specialized "
        "practice of safely re-engaging dormant subscribers while protecting sender reputation and deliverability."
    ))
    story.append(sp(10))

    story.append(p(
        f'<font color="{TEAL.hexval()}">Contact: chuck@expert.email  \u2022  Web: Expert.Email</font>'
    ))

    # ── Build with page templates ─────────────────────────────
    class PhantomDoc(BaseDocTemplate):
        def __init__(self, filename, **kwargs):
            BaseDocTemplate.__init__(self, filename, **kwargs)
            frame = Frame(margin, inch * 0.85, avail_w, H - inch * 1.6,
                          id='normal')
            cover_frame = Frame(0, 0, W, H, id='cover',
                                leftPadding=0, rightPadding=0,
                                topPadding=0, bottomPadding=0)
            self.addPageTemplates([
                PageTemplate(id='Cover', frames=cover_frame, onPage=CoverPage.draw),
                PageTemplate(id='Content', frames=frame, onPage=ContentPage.draw),
            ])

    doc = PhantomDoc(out_path, pagesize=letter)

    final_story = [story[0]]  # Cover spacer
    final_story.append(NextPageTemplate('Content'))
    final_story.extend(story[1:])

    doc.build(final_story)
    print(f"\n  Generated: {out_path}")
    print(f"  URL used:  {TOOL_URL}")
    print(f"  To customise for a partner, run:")
    print(f"    python3 generate_phantom_engaged.py \"https://partner-tracking-link.com\"\n")
    return out_path

if __name__ == "__main__":
    build()
