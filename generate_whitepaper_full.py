#!/usr/bin/env python3
"""
Phantom Engaged Whitepaper Generator - Full Version
===================================================
Design match: landing page (index.html)
Content: Full v4 text + correct callout placements

Usage:
  python3 generate_whitepaper_full.py [TOOL_URL]
"""

import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, Flowable, Frame, 
    BaseDocTemplate, PageTemplate, NextPageTemplate, Table, TableStyle,
    KeepTogether, Image
)
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# ── Config ──────────────────────────────────────────────────
TOOL_URL = sys.argv[1] if len(sys.argv) > 1 else "https://expert.email/classify"
OUTPUT   = sys.argv[2] if len(sys.argv) > 2 else "Phantom_Engaged_Whitepaper_Full.pdf"
VERSION  = "5.0"
DATE     = "February 2026"

# ── Design Tokens (from index.html) ──────────────────────────
DARK_BG     = HexColor("#1C2A3A")
DARK_BG_ALT = HexColor("#1F3044") # Lighter dark for usage in callouts on dark bg
TEAL        = HexColor("#2BA5A5")
TEAL_HOVER  = HexColor("#34BFBF")
TEAL_MUTED  = HexColor("#EBF6F6")
TEXT_BODY   = HexColor("#2D3E50")
TEXT_MUTED  = HexColor("#8A9BB5")
OFF_WHITE   = HexColor("#F7F8FA")
BORDER_SUBTLE = HexColor("#E2E6EC")
COVER_TEXT_MUTED = HexColor("#B0C4CE") # Lighter muted for dark background

# ── Dimensions ───────────────────────────────────────────────
W, H = letter
MARGIN = inch * 1.0

# ── Styles ───────────────────────────────────────────────────
sNormal = ParagraphStyle(
    "sNormal", fontName="Helvetica", fontSize=11, leading=17,
    textColor=TEXT_BODY, alignment=TA_JUSTIFY, spaceAfter=10,
)

sBullet = ParagraphStyle(
    "sBullet", parent=sNormal, leftIndent=20, bulletIndent=8,
    spaceBefore=4, spaceAfter=4,
)

sH1 = ParagraphStyle(
    "sH1", fontName="Helvetica-Bold", fontSize=24, leading=28,
    textColor=DARK_BG, spaceAfter=16, spaceBefore=24,
)

sH2 = ParagraphStyle(
    "sH2", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=DARK_BG, spaceAfter=10, spaceBefore=18,
)

sH3 = ParagraphStyle(
    "sH3", fontName="Helvetica-Bold", fontSize=12, leading=16,
    textColor=TEAL, spaceAfter=4, spaceBefore=20, # Increased spaceBefore for better separation
)

sCalloutText = ParagraphStyle(
    "sCalloutText", fontName="Helvetica-Oblique", fontSize=11,
    leading=16, textColor=TEXT_BODY, alignment=TA_LEFT,
)

sCalloutNormal = ParagraphStyle(
    "sCalloutNormal", fontName="Helvetica", fontSize=11,
    leading=16, textColor=TEXT_BODY, alignment=TA_LEFT,
)

sRef = ParagraphStyle(
    "sRef", fontName="Helvetica", fontSize=9, leading=13,
    textColor=TEXT_MUTED, spaceAfter=4,
)

# Table Styles
sTableHdr = ParagraphStyle(
    "sTableHdr", fontName="Helvetica-Bold", fontSize=10, leading=12,
    textColor=white, alignment=TA_LEFT,
)
sTableCell = ParagraphStyle(
    "sTableCell", fontName="Helvetica", fontSize=10, leading=14,
    textColor=TEXT_BODY, alignment=TA_LEFT,
)
sTableBoldCell = ParagraphStyle(
    "sTableBoldCell", fontName="Helvetica-Bold", fontSize=10, leading=14,
    textColor=TEXT_BODY, alignment=TA_LEFT,
)

# ── Custom Flowables ────────────────────────────────────────
class ModernCallout(Flowable):
    """
    Landing page .callout style
    """
    def __init__(self, text_items, width):
        Flowable.__init__(self)
        self.width = width
        self.bg = TEAL_MUTED
        self.border_color = TEAL
        self.padding = 18
        
        self.paras = []
        if isinstance(text_items, str):
            text_items = [text_items]
            
        for t in text_items:
            # Check if t is tuple (text, style)
            if isinstance(t, tuple):
                self.paras.append(Paragraph(t[0], t[1]))
            else:
                self.paras.append(Paragraph(t, sCalloutText))
                
        self.inner_w = width - (self.padding * 2) - 4
        
        total_h = 0
        for p in self.paras:
            _, ph = p.wrap(self.inner_w, 1000)
            total_h += ph + 10 # spacing between paras
            
        self.height = total_h - 10 + (self.padding * 2) # remove last spacing

    def draw(self):
        c = self.canv
        # Background
        c.setFillColor(self.bg)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        # Left Border
        c.setFillColor(self.border_color)
        c.rect(0, 0, 4, self.height, fill=1, stroke=0)
        
        # Draw paragraphs
        y = self.height - self.padding
        x = 4 + self.padding
        for p in self.paras:
            _, ph = p.wrap(self.inner_w, 1000)
            p.drawOn(c, x, y - ph)
            y -= (ph + 10)

class OverlapDiagram(Flowable):
    """Recreation of the intersection diagram, cleaner style."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.width = width
        self.height = 110 # Slightly taller for better spacing
    
    def draw(self):
        d = Drawing(self.width, self.height)
        cx = self.width / 2
        cy = self.height / 2 + 10
        
        # Bars dimensions
        bar_w = 420
        bar_h = 56
        x_start = cx - (bar_w/2)
        y_start = cy - (bar_h/2)
        
        # 1. Base Dark Bar (representing full spectrum)
        d.add(Rect(x_start, y_start, bar_w, bar_h, rx=4, ry=4, fillColor=DARK_BG, strokeWidth=0))
        
        # 2. Phantom Zone (Middle overlap)
        # We'll make it a distinct lighter section in the middle
        phantom_w = 160
        phantom_x = cx - (phantom_w/2)
        
        d.add(Rect(phantom_x, y_start, phantom_w, bar_h, fillColor=TEAL_MUTED, strokeColor=TEAL, strokeWidth=2))
        
        # 3. Labels
        # Left: Engaged
        d.add(String(x_start + 65, y_start + (bar_h/2) - 4, "ENGAGED", textAnchor="middle", fillColor=white, fontName="Helvetica-Bold", fontSize=11))
        
        # Right: Unengaged
        d.add(String(x_start + bar_w - 65, y_start + (bar_h/2) - 4, "UNENGAGED", textAnchor="middle", fillColor=TEXT_MUTED, fontName="Helvetica-Bold", fontSize=11))
        
        # Middle: Phantom
        d.add(String(cx, y_start + (bar_h/2) + 4, "PHANTOM ENGAGED", textAnchor="middle", fillColor=TEAL, fontName="Helvetica-Bold", fontSize=11))
        d.add(String(cx, y_start + (bar_h/2) - 10, "(Uncertainty)", textAnchor="middle", fillColor=TEAL, fontName="Helvetica", fontSize=9))
        
        # Subtitle text below diagram
        d.add(String(cx, y_start - 20, "Privacy protections increase the overlap between what we can measure and what is real.",
                     textAnchor="middle", fillColor=TEXT_MUTED, fontName="Helvetica-Oblique", fontSize=9))

        renderPDF.draw(d, self.canv, 0, 0)

# ── Helpers ──────────────────────────────────────────────────
def sec(title):
    return [Paragraph(title, sH1)]

def subsec(title):
    return [Paragraph(title, sH2)]

def h3(title):
    return [Paragraph(title, sH3)]

def p(text, style=sNormal):
    return Paragraph(text, style)

def sp(h=12):
    return Spacer(1, h)

def bullet(text):
    return Paragraph(f"\u2022  {text}", sBullet)

# ── Page Templates ──────────────────────────────────────────
def draw_cover(canvas, doc):
    canvas.saveState()
    # Full dark background
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    
    # Layout constants based on v4 screenshot
    LINE_X = inch * 1.2
    TEXT_X = LINE_X + 24
    CONTENT_Y_START = H * 0.75  # Start title around upper third
    
    # Vertical Line (Thinner teal line)
    # Extends further down now due to the bottom blurb
    canvas.setFillColor(TEAL)
    canvas.rect(LINE_X, inch * 1.5, 2, H - inch * 2.5, fill=1, stroke=0)
    
    # Title
    canvas.setFont("Helvetica-Bold", 48) # Larger, bold
    canvas.setFillColor(white)
    canvas.drawString(TEXT_X, CONTENT_Y_START, "Phantom")
    canvas.drawString(TEXT_X, CONTENT_Y_START - 56, "Engaged")
    
    # Description
    canvas.setFont("Helvetica", 12)
    canvas.setFillColor(COVER_TEXT_MUTED)
    
    desc_y = CONTENT_Y_START - 100
    canvas.drawString(TEXT_X, desc_y, "A position paper on the invisible overlap between")
    canvas.drawString(TEXT_X, desc_y - 18, "engaged and disengaged subscribers created by")
    canvas.drawString(TEXT_X, desc_y - 36, "modern email privacy protections")
    
    # Horizontal Divider
    div_y = desc_y - 70
    canvas.setStrokeColor(HexColor("#2C3E50")) # Subtle divider
    canvas.setLineWidth(1)
    # canvas.line(TEXT_X, div_y, W - inch *1.5, div_y) # Removed divider to match clean look if preferred, keeping as per previous update request
    canvas.line(TEXT_X, div_y, W - inch *1.5, div_y)
    
    # Footer / Meta (Name, Company, Version)
    meta_y_start = div_y - 30
    
    # Name
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(TEAL)
    canvas.drawString(TEXT_X, meta_y_start, "Chuck Mullaney")
    
    # Company
    canvas.setFont("Helvetica", 11)
    canvas.setFillColor(COVER_TEXT_MUTED)
    canvas.drawString(TEXT_X, meta_y_start - 18, "Expert.Email")
    
    # Version / Date
    canvas.drawString(TEXT_X, meta_y_start - 36, f"Version {VERSION} \u2022 {DATE}")

    # -- Bottom Callout / Blurb --
    # "When privacy protections break open tracking..."
    
    blurb_text = (
        "When privacy protections break open tracking, a large portion of your list becomes "
        "impossible to classify using email analytics alone. That invisible overlap is the "
        "<b>Phantom Engaged</b> problem: people who look engaged in reports but may or may "
        "not be paying attention."
    )
    
    blurb_w = W - TEXT_X - inch*1.5 # Available width
    blurb_style = ParagraphStyle(
        "Blurb", fontName="Helvetica", fontSize=11, leading=16,
        textColor=HexColor("#D0D0D0"), # Lighter grey text
        alignment=TA_LEFT
    )
    
    p = Paragraph(blurb_text, blurb_style)
    w, h = p.wrap(blurb_w - 40, 1000) # -40 for padding
    
    # Box Positioning
    box_h = h + 40
    box_y = inch * 2.5 # Position near bottom, above copyright
    
    # Background Box
    canvas.setFillColor(DARK_BG_ALT)
    canvas.rect(TEXT_X, box_y, blurb_w, box_h, fill=1, stroke=0)
    
    # Left Border
    canvas.setFillColor(TEAL)
    canvas.rect(TEXT_X, box_y, 4, box_h, fill=1, stroke=0)
    
    # Text
    p.drawOn(canvas, TEXT_X + 20, box_y + 20)
    
    # -- Copyright Footer --
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(HexColor("#546E7A")) # Dark muted
    canvas.drawString(TEXT_X, inch * 1.5, "© 2026 Chuck Mullaney. You may share this document in full with attribution.")
    
    # Restore State
    canvas.restoreState()

def draw_content_page(canvas, doc):
    canvas.saveState()
    # Footer
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN, inch*0.5, f"Phantom Engaged Position Paper v{VERSION}")
    canvas.drawRightString(W - MARGIN, inch*0.5, f"Page {doc.page} | Expert.Email")
    
    # Divider line
    canvas.setStrokeColor(BORDER_SUBTLE)
    canvas.setLineWidth(1)
    canvas.line(MARGIN, inch*0.65, W - MARGIN, inch*0.65)
    
    canvas.restoreState()

# ── Build ───────────────────────────────────────────────────
def build():
    doc = BaseDocTemplate(OUTPUT, pagesize=letter)
    
    # Frames
    frame_cover = Frame(0, 0, W, H, id='cover', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_content = Frame(MARGIN, MARGIN, W - 2*MARGIN, H - 2*MARGIN, id='content')
    
    doc.addPageTemplates([
        PageTemplate(id='Cover', frames=frame_cover, onPage=draw_cover),
        PageTemplate(id='Content', frames=frame_content, onPage=draw_content_page),
    ])
    
    story = []
    avail_w = W - 2*MARGIN
    
    # -- Cover --
    story.append(NextPageTemplate('Content'))
    story.append(PageBreak())
    
    # -- Executive Summary --
    # Keep title and first intro paragraph together
    story.append(KeepTogether(sec("Executive Summary") + [
        p("For years, marketers treated opens as a proxy for attention. Now, that proxy is unreliable.")
    ]))
    
    story.append(sp())
    story.append(p("Apple Mail Privacy Protection (MPP) is designed to prevent senders from learning about Mail activity by downloading remote content in the background, not only when someone views the message, and by obscuring IP based inference. [1][2]"))
    story.append(sp())
    story.append(p("This shift creates a practical failure mode: you can no longer confidently distinguish between a quiet, loyal reader and a truly disengaged recipient whose client triggered tracking anyway. Those two people collapse into the same reporting bucket when you rely on opens."))
    story.append(sp())
    
    # Keep classification stance para and the callout together
    story.append(KeepTogether([
        p("This collapse goes beyond analytics. It causes real list damage when marketers run re-engagement or suppression based on signals that no longer map cleanly to human attention. In the post privacy world, the highest inbox deliverability risk isn't the subscribers you can clearly identify as inactive. It's the subscribers who <i>appear</i> active but whose attention cannot be verified."),
        sp(16),
        ModernCallout(
            "Phantom Engaged is the name for that uncertainty bucket: an unavoidable overlap created when privacy protections break our ability to distinguish silence from disengagement using email metrics alone.",
            avail_w
        ),
        sp(16),
        p("The solution isn't a clever new metric. It's a classification stance: use intentional actions as proof of engagement, treat opens as weak evidence, and handle ambiguity conservatively to avoid irreversible harm.")
    ]))
    
    # -- Section 1 --
    story.append(KeepTogether(sec("1. What Changed in Measurement") + [
        p("Modern inboxes are built to protect recipients from hidden tracking. Apple\u2019s approach is the most explicit: when a user enables Protect Mail Activity, remote content is privately downloaded in the background when the email is received, rather than when it is viewed, helping prevent senders from learning about Mail activity. [1][2]"),
        sp(),
        p("For marketers, this background fetch is the core issue. The tracking pixel may load even if the person never intentionally opened the email. Many email platforms now expose indicators for machine generated opens or MPP related opens for this reason (for example, SendGrid\u2019s MPP flag). [3]")
    ]))
    
    story.append(sp())
    story.append(KeepTogether([
        p("At the same time, mailbox providers are tightening sender expectations around authentication, one click unsubscribe, and complaint thresholds. [4][5] The ecosystem is simultaneously becoming less measurable and less forgiving."),
        sp(16),
        ModernCallout([
            ("<b>The Tension:</b> <i>You're being asked to prove you send wanted mail while losing the cleanest historical proxy (opens) that many teams relied on to define \u2018wanted.\u2019</i>", sCalloutNormal)
        ], avail_w)
    ]))
    
    # -- Section 2 --
    story.append(KeepTogether(sec("2. Why the Open Event No Longer Means Attention") + [
        p("Opens were always an indirect measurement. Even before MPP, they depended on image loading, mail client settings, caching behaviors, security tools, and link scanning. Privacy protections push this from \u2018imperfect\u2019 to \u2018structurally unreliable\u2019 for classification purposes.")
    ]))
    story.append(sp(10))
    
    # Signal Table - NEVER split a table or separate it from its intro
    tdata = [
        [Paragraph("Signal", sTableHdr), Paragraph("Pre-Privacy Implication", sTableHdr), Paragraph("Post-Privacy Reality", sTableHdr)],
        [Paragraph("Open", sTableBoldCell), Paragraph("A person likely viewed the email.", sTableCell), Paragraph("Often means the mail client fetched images. May happen without a human reading.", sTableCell)],
        [Paragraph("No open", sTableBoldCell), Paragraph("A person likely did not view the email.", sTableCell), Paragraph("Could be a non reader, or a reader whose mail client blocks tracking.", sTableCell)],
        [Paragraph("Click", sTableBoldCell), Paragraph("A person intentionally acted.", sTableCell), Paragraph("Still the cleanest proof of intent in email. Not perfect, but far stronger than opens.", sTableCell)],
        [Paragraph("Reply", sTableBoldCell), Paragraph("A person intentionally engaged.", sTableCell), Paragraph("High confidence intent signal. May bypass link blockers and tracking limitations.", sTableCell)],
        [Paragraph("Purchase / login", sTableBoldCell), Paragraph("Downstream proof of value.", sTableCell), Paragraph("Best proof if you can connect it. The gold standard for classification.", sTableCell)],
    ]
    col_w = [avail_w * 0.18, avail_w * 0.35, avail_w * 0.47]
    t = Table(tdata, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, -1), OFF_WHITE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_SUBTLE),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    # Wrap table in KeepTogether with the callout following it
    story.append(KeepTogether([
        t,
        sp(16),
        ModernCallout(
            "If you take one thing from this paper, take this: opens are now evidence that something rendered remote content, not evidence that a person noticed, read, agreed, or wanted more.",
            avail_w
        )
    ]))

    # -- Section 3 --
    # Start Section 3 on a new page if it's getting low, but KeepTogether might handle it
    story.append(KeepTogether(sec("3. The Phantom Engaged Overlap") + [
        p("In a pre privacy mental model, the list felt cleanly separable: engaged subscribers showed opens and clicks; disengaged subscribers went dark. In the post privacy model, measurement pushes a large number of people into the same middle zone: visible activity without confirmable intent."),
        sp(),
        OverlapDiagram(avail_w),
        sp(),
        p("This overlap isn't a new segment you can optimize away. It's a fact of measurement uncertainty. Attempting to force certainty (for example, by treating opens as attention regardless) is where most classification mistakes begin."),
        sp(8),
        p("Phantom Engaged isn't just a deliverability problem. It’s a revenue problem. Some of your highest value subscribers live here. These are people who consistently read but rarely click, reply, or trigger trackable events. In many niches, \u201Cquiet readers\u201D become your best buyers when the offer matches the moment. Treating Phantom Engaged as \u201Cless engaged\u201D by default can reduce the very exposure that converts them, creating hidden revenue loss that looks like \u201Ccleaner engagement\u201D in dashboards. Phantom Engaged exists to protect both sides of the risk: sender reputation and the silent loyalty that produces long term value.")
    ]))

    # -- Section 4 --
    # This is a complex section with a big table and callout. 
    # Better to force a page break here to ensure the table and framework start clean.
    story.append(PageBreak())
    
    story.extend(sec("4. A Classification Framework That Admits Uncertainty"))
    story.append(p("Most engagement models assume clean boundaries. The A/B/C framework starts from the opposite premise: uncertainty is the default state, and the burden of proof falls on the signals, not on the subscriber. It's intentionally conservative, designed to protect silent readers and prevent irreversible decisions based on noisy data."))
    story.append(sp(10))
    
    # A/B/C Table
    abc_data = [
        [Paragraph("", sTableHdr), Paragraph("Classification", sTableHdr), Paragraph("Signals", sTableHdr), Paragraph("Treatment", sTableHdr)],
        [Paragraph("<font size='14' color='#2BA5A5'>A</font>", sTableBoldCell), Paragraph("Confirmed Intent", sTableBoldCell), Paragraph("Clicks, replies, purchases, logins. Opens optional.", sTableCell), Paragraph("Send with confidence. These subscribers have demonstrated attention.", sTableCell)],
        [Paragraph("<font size='14' color='#2BA5A5'>B</font>", sTableBoldCell), Paragraph("Phantom (Uncertain)", sTableBoldCell), Paragraph("Opens present. No intentional actions. Ambiguous by design.", sTableCell), Paragraph("Handle conservatively. This is a holding state, not a verdict.", sTableCell)],
        [Paragraph("<font size='14' color='#2BA5A5'>C</font>", sTableBoldCell), Paragraph("Unengaged (Observable)", sTableBoldCell), Paragraph("No opens, clicks, replies, or actions within a window.", sTableCell), Paragraph("Eligible for controlled, finite re-engagement or suppression.", sTableCell)],
    ]
    abc_col = [avail_w * 0.08, avail_w * 0.20, avail_w * 0.36, avail_w * 0.36]
    at = Table(abc_data, colWidths=abc_col)
    at.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, -1), OFF_WHITE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_SUBTLE),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
    ]))
    
    # Keep table and its explanatory note together
    story.append(KeepTogether([
        at,
        sp(10),
        p("<b>Important:</b> Bucket B isn't a behavior segment or a personality type. It's a holding state that says: \u201CWe don\u2019t currently have enough proof to classify this person as engaged or disengaged.\u201D Treating it as anything else defeats its purpose.")
    ]))
    
    story.append(sp(16))
    
    # Callout A - Keep with Section 4
    callout_a_text = [
        (f"<b>Apply this framework to your list.</b> We built a <a href='{TOOL_URL}' color='{TEAL.hexval()}'>free classification tool</a> "
         "to help you map your subscribers into the A/B/C framework described above. <b>There is no opt in and no paywall.</b> It's just a practical starting point for teams "
         "ready to move from open based assumptions to intent based classification.",
         sCalloutNormal)
    ]
    story.append(ModernCallout(callout_a_text, avail_w))
    story.append(sp(16))
    
    # -- Section 5 --
    story.extend(sec("5. What Goes Wrong When You Ignore the Uncertainty"))
    story.append(p("Most list harm in the post privacy era happens when teams apply pre privacy rules to post privacy signals. These mistakes are common, understandable, and worth naming clearly so you can recognize them in your own program:"))
    
    # Keep list together
    story.append(KeepTogether([
        bullet("<b>Resend to non openers becomes a frequency amplifier.</b> What was once a relevance tactic now adds volume to inboxes that may already be receiving your emails, just without generating a trackable open."),
        bullet("<b>Aggressive \u201Clast chance\u201D campaigns pressure silent readers.</b> When quiet loyalty looks identical to disengagement in your data, urgency based re engagement risks pushing away people who were still paying attention."),
        bullet("<b>Open based suppression quietly removes high value subscribers.</b> Readers whose mail clients block tracking or who consume emails without triggering pixels get sorted into your inactive bucket, and deleted."),
        bullet("<b>Dashboard confidence replaces relationship awareness.</b> Teams over trust reporting and under trust what they know about long term customer behavior and brand affinity.")
    ]))
    
    story.append(sp())
    story.append(KeepTogether([
        p("These errors are rarely visible in the moment because the reporting still looks healthy. The cost shows up over time: higher complaint rates, weaker inbox placement, reduced conversion, and a list that grows harder to recover."),
        sp(),
        ModernCallout([
            "Phantom Engaged is why modern re-engagement is primarily a risk management problem. The most important decisions are about what you choose <b>not</b> to do when you cannot know the full truth from email metrics alone."
        ], avail_w)
    ]))

    # -- Section 6 --
    # Force page break to start principles cleanly
    story.append(PageBreak())
    
    story.extend(sec("6. Principles for Working Marketers"))
    story.append(p("These are principles, not tactics. Tactics change with platforms and tools. Principles hold up regardless of which ESP you use or how large your list is."))
    
    # Keep each principle and its description together
    story.append(KeepTogether(subsec("Principle 1: Intentional proof beats inferred attention.") + [
        p("Clicks, replies, purchases, logins, and other downstream events are not perfect, but they reflect deliberate action. Build your classification around these signals first. Treat opens as supporting evidence, not as the foundation.")
    ]))
    
    story.append(KeepTogether(subsec("Principle 2: When you are uncertain, restraint is a strategy.") + [
        p("When you cannot safely distinguish a loyal quiet reader from a non-reader, pressure and urgency-based tactics carry real risk. It is better to reduce frequency, adjust content, or route people into lower-pressure paths than to gamble trust for short-term clarity.")
    ]))
    
    story.append(KeepTogether(subsec("Principle 3: Classify first, optimize second.") + [
        p("Optimization assumes your labels are correct. In the post-privacy world, those labels are often wrong. Invest in building a truthful classification stance before chasing marginal KPI lifts. The returns from accurate classification will outperform the returns from optimizing against flawed segments.")
    ]))
    
    story.append(KeepTogether(subsec("Principle 4: Lock your observation windows before judging.") + [
        p("An observation window is the amount of time you commit to watching for an intentional signal before changing how you treat someone. Set it in advance. Without a fixed window, it is easy to unconsciously move the goalposts to match whatever story your dashboard is telling that week. A locked window turns engagement policy into a fair, repeatable process.")
    ]))
    
    story.append(KeepTogether(subsec("Principle 5: Prefer reversible actions over irreversible ones.") + [
        p("When you are unsure, choose actions you can undo. Reducing frequency, changing content, or moving people into a different sending cadence are all reversible. Suppression and permanent removal are not. Save irreversible decisions for situations where you have high confidence.")
    ]))
    
    # -- Section 7 --
    story.append(KeepTogether(sec("7. A Note on Ethics and Privacy") + [
        p("Phantom Engaged is not a call to outsmart privacy protections. Those protections exist because recipients deserve control over how they are tracked. The appropriate response is to adapt how we interpret metrics and how we treat people, not to find clever workarounds.")
    ]))
    
    story.append(KeepTogether([
        p("This paper takes a clear stance on where the line should be:"),
        bullet("Deceptive workarounds designed to recreate individual-level surveillance undermine the trust that makes email marketing sustainable."),
        bullet("People should not be penalized for failing to produce trackable signals. Silence is not the same as rejection."),
        bullet("Manufacturing urgency to force clicks as a \u201Cproof of life\u201D mechanism treats subscribers as problems to solve rather than people to serve."),
        bullet("The better path is consent-based: clear expectations, easy unsubscribe, and content that earns attention on its own merits.")
    ]))
    
    story.append(sp())
    story.append(p("This stance also aligns with the direction mailbox providers are heading: easier unsubscribe, stronger authentication requirements, and lower tolerance for unwanted mail. [4][5] Working with that trajectory, rather than against it, is both the ethical choice and the practical one."))

    # -- Section 8 --
    story.extend(sec("8. What Competent Teams Do Next"))
    story.append(p("This isn't a campaign checklist. It's a governance upgrade: changes to the rules your email program runs on."))
    
    # Group h3 + paragraph
    story.append(KeepTogether(h3("Adopt a measurement hierarchy.") + [
        p("Write down, in order, which signals you trust most for engagement classification. In most programs, downstream events and replies outrank clicks, and clicks outrank opens. Having this documented means your team makes consistent decisions instead of defaulting to whatever metric is easiest to pull.")
    ]))
    
    story.append(KeepTogether(h3("Separate deliverability safety from performance reporting.") + [
        p("Your dashboard is a performance tool. It should not be the final authority on who stays and who goes. Deliverability safety policies should be conservative by default and should explicitly account for the uncertainty that privacy inflated opens create.")
    ]))
    
    story.append(KeepTogether(h3("Design for silent readers.") + [
        p("Accept that a meaningful percentage of your audience will never click but still receives value from your emails. If your program requires clicking to avoid being treated as inactive, your program is hostile to a real segment of real people. That is worth examining.")
    ]))
    
    story.append(KeepTogether(h3("Reduce emotional automation.") + [
        p("Revisit any automation that interprets silence as rejection. In the post privacy world, silence is often just silence, not a statement about your brand, your content, or your value.")
    ]))
    
    story.append(KeepTogether(h3("Invest in proof where it actually exists.") + [
        p("Where feasible, connect email to outcomes you can verify: purchases, logins, subscription renewals, product usage. This is not about surveilling individuals. It is about ensuring you are not mistaking a privacy artifact for actual disengagement.")
    ]))

    # -- Conclusion & References --
    # Ensure Conclusion starts on a new page or at least cleanly separated
    story.append(PageBreak())
    
    story.extend(sec("Conclusion"))
    story.append(p("Phantom Engaged is the name for a reality email marketers can no longer afford to ignore: a large portion of your list now sits in an overlap where the most common engagement signal (opens) is not trustworthy proof of attention."))
    story.append(p("The correct response is not panic, and it is not denial. It is classification discipline: prove intent where you can, admit uncertainty where you must, and treat that uncertainty with restraint."))
    
    story.append(sp(8))
    
    # Keep final callout and "Put This Into Practice" together
    final_callout = [
        ("<b>If you share one sentence with your team, share this:</b>", sCalloutNormal),
        ("<i>Stop asking your dashboards to answer a question they can no longer answer. Replace false certainty with policies that protect trust and list health.</i>", sCalloutText),
    ]
    story.append(ModernCallout(final_callout, avail_w))
    story.append(sp(16))

     # -- Callout C (Embedded) --
    story.append(KeepTogether(subsec("Put This Into Practice") + [
        p("The ideas in this paper become useful when you apply them to your own subscriber data. To make that starting point easier, we built a free tool that walks you through the A/B/C classification framework described in Section 4."),
        p(f"<b>There is no opt in, no paywall, and no sales pitch.</b> It exists to help working marketers put classification discipline into practice. <a href='{TOOL_URL}' color='{TEAL.hexval()}'>Access the free tool here.</a>")
    ]))
    story.append(sp(16))

    # -- References & Author -- 
    # Can sit on same page as conclusion if room, or next
    story.append(KeepTogether([
        Paragraph("References", sH2),
    ]))
    refs = [
        '[1] Apple. "Mail Privacy Protection & Privacy." Apple Legal.',
        '[2] Apple Support. "Use Mail Privacy Protection on Mac."',
        '[3] Twilio SendGrid Docs. "Understanding Apple Mail Privacy Protection and Open Events"',
        '[4] Google Workspace Admin Help. "Email sender guidelines"',
        '[5] Yahoo. "Sender Best Practices"',
    ]
    for r in refs:
        story.append(Paragraph(r, sRef))
        
    story.append(sp(16))
    
    # -- About Author --
    story.append(KeepTogether([
        Paragraph("About the Author", sH2),
        p("Chuck Mullaney brings 25 years of digital marketing expertise, with 15 years dedicated exclusively to email marketing and inbox deliverability. He has architected six email platforms, gaining unique insight into the email strategies of 26,000 businesses. This rare vantage point has given him comprehensive experience in the specialized practice of safely re engaging dormant subscribers while protecting sender reputation."),
        sp(8),
        Paragraph(f'<font color="{TEAL.hexval()}">Contact: chuck@expert.email  |  Web: Expert.Email</font>', sNormal)
    ]))

    doc.build(story)
    print(f"Generated: {OUTPUT}")

if __name__ == "__main__":
    build()
