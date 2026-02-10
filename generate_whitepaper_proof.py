#!/usr/bin/env python3
"""
Phantom Engaged Whitepaper Generator - Proof of Concept
=====================================================
Design match: landing page (index.html)
Style: Professional White Paper / Report
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, Flowable, Frame, 
    BaseDocTemplate, PageTemplate, NextPageTemplate
)
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# ── Design Tokens (from index.html) ──────────────────────────
DARK_BG     = HexColor("#1C2A3A")
TEAL        = HexColor("#2BA5A5")
TEAL_MUTED  = HexColor("#EBF6F6")  # Light version of teal for callout BG
TEXT_BODY   = HexColor("#2D3E50")
TEXT_MUTED  = HexColor("#8A9BB5")
OFF_WHITE   = HexColor("#F7F8FA")

# ── Dimensions ───────────────────────────────────────────────
W, H = letter
MARGIN = inch * 1.0

# ── Styles ───────────────────────────────────────────────────
sNormal = ParagraphStyle(
    "sNormal", fontName="Helvetica", fontSize=11, leading=17,
    textColor=TEXT_BODY, alignment=TA_JUSTIFY, spaceAfter=10,
)

sH1 = ParagraphStyle(
    "sH1", fontName="Helvetica-Bold", fontSize=24, leading=28,
    textColor=DARK_BG, spaceAfter=16, spaceBefore=24,
)

sH2_Dark = ParagraphStyle(
    "sH2_Dark", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=white, spaceAfter=12, spaceBefore=6,
)

sH2 = ParagraphStyle(
    "sH2", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=DARK_BG, spaceAfter=10, spaceBefore=18,
)

sCalloutText = ParagraphStyle(
    "sCalloutText", fontName="Helvetica-Oblique", fontSize=11,
    leading=16, textColor=TEXT_BODY, alignment=TA_LEFT,
)

sFooter = ParagraphStyle(
    "sFooter", fontName="Helvetica", fontSize=8, leading=10,
    textColor=TEXT_MUTED,
)

# ── Custom Flowables ────────────────────────────────────────
class ModernCallout(Flowable):
    """
    Matches landing page .callout style:
    - Left border: 4px solid TEAL
    - Background: TEAL_MUTED
    - Padding: Ample
    """
    def __init__(self, text, width):
        Flowable.__init__(self)
        self.width = width
        self.text = text
        self.bg = TEAL_MUTED
        self.border_color = TEAL
        self.padding = 18
        
        # Wrap text
        self.p = Paragraph(text, sCalloutText)
        self.inner_w = width - (self.padding * 2) - 4 # 4 is border width
        _, self.h = self.p.wrap(self.inner_w, 1000)
        self.height = self.h + (self.padding * 2)

    def draw(self):
        c = self.canv
        # Background
        c.setFillColor(self.bg)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        # Left Border
        c.setFillColor(self.border_color)
        c.rect(0, 0, 4, self.height, fill=1, stroke=0)
        # Text
        self.p.drawOn(c, 4 + self.padding, self.padding)

class OverlapDiagram(Flowable):
    """Recreation of the intersection diagram, cleaner style."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.width = width
        self.height = 100
    
    def draw(self):
        d = Drawing(self.width, self.height)
        # Simplified representation for proof
        cx = self.width / 2
        cy = self.height / 2
        
        # Two overlapping circles logic represented as bars nicely
        # Draw base bar
        bar_w = 400
        bar_h = 50
        x_start = cx - (bar_w/2)
        y_start = cy - (bar_h/2)
        
        # Engaged (Left)
        d.add(Rect(x_start, y_start, 120, bar_h, fillColor=DARK_BG, strokeWidth=0))
        d.add(String(x_start + 60, y_start + 20, "ENGAGED", textAnchor="middle", fillColor=white, fontName="Helvetica-Bold", fontSize=10))
        
        # Phantom (Middle - Overlap)
        d.add(Rect(x_start + 120, y_start, 160, bar_h, fillColor=TEAL_MUTED, strokeColor=TEAL, strokeWidth=2))
        d.add(String(x_start + 200, y_start + 28, "PHANTOM ENGAGED", textAnchor="middle", fillColor=TEAL, fontName="Helvetica-Bold", fontSize=10))
        d.add(String(x_start + 200, y_start + 15, "(Uncertainty)", textAnchor="middle", fillColor=TEAL, fontName="Helvetica", fontSize=8))

        # Unengaged (Right)
        d.add(Rect(x_start + 280, y_start, 120, bar_h, fillColor=DARK_BG, strokeWidth=0))
        d.add(String(x_start + 340, y_start + 20, "UNENGAGED", textAnchor="middle", fillColor=TEXT_MUTED, fontName="Helvetica-Bold", fontSize=10))

        renderPDF.draw(d, self.canv, 0, 0)

# ── Page Templates ──────────────────────────────────────────
def draw_cover(canvas, doc):
    canvas.saveState()
    # Full dark background
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    
    # Hero Accent Line (matches landing page hero::before)
    canvas.setFillColor(TEAL)
    canvas.rect(inch*1.0, inch*1.5, 4, H - inch*3, fill=1, stroke=0)
    
    # Title
    canvas.setFont("Helvetica-Bold", 42)
    canvas.setFillColor(white)
    canvas.drawString(inch*1.4, H - inch*3, "Phantom")
    canvas.drawString(inch*1.4, H - inch*3.6, "Engaged")
    
    # Subtitle
    canvas.setFont("Helvetica", 16)
    canvas.setFillColor(TEAL)
    canvas.drawString(inch*1.4, H - inch*4.2, "\u2014 The Subscribers Your Dashboard Can't Classify")
    
    # Author / Meta
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(white)
    canvas.drawString(inch*1.4, inch*1.5, "Chuck Mullaney  |  Expert.Email")
    
    canvas.restoreState()

def draw_content_page(canvas, doc):
    canvas.saveState()
    # Footer
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN, inch*0.5, "Phantom Engaged Position Paper")
    canvas.drawRightString(W - MARGIN, inch*0.5, f"Page {doc.page} | Expert.Email")
    canvas.restoreState()

# ── Build ───────────────────────────────────────────────────
def build_proof():
    doc = BaseDocTemplate("Phantom_Engaged_Whitepaper_Proof.pdf", pagesize=letter)
    
    # Frames
    frame_cover = Frame(0, 0, W, H, id='cover', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_content = Frame(MARGIN, MARGIN, W - 2*MARGIN, H - 2*MARGIN, id='content')
    
    doc.addPageTemplates([
        PageTemplate(id='Cover', frames=frame_cover, onPage=draw_cover),
        PageTemplate(id='Content', frames=frame_content, onPage=draw_content_page),
    ])
    
    story = []
    
    # -- Page 1: Cover --
    story.append(NextPageTemplate('Content'))
    story.append(PageBreak())
    
    # -- Page 2: Executive Summary --
    story.append(Paragraph("Executive Summary", sH1))
    story.append(Paragraph(
        "For years, marketers treated opens as a proxy for attention. That proxy is now unreliable at scale. "
        "Apple Mail Privacy Protection (MPP) is designed to prevent senders from learning about Mail activity by "
        "downloading remote content in the background, not only when someone views the message.",
        sNormal
    ))
    story.append(Paragraph(
        "This shift creates a practical failure mode: you can no longer confidently distinguish between a quiet, "
        "loyal reader and a truly disengaged recipient whose client triggered tracking anyway.",
        sNormal
    ))
    
    # Callout Example
    story.append(Spacer(1, 12))
    story.append(ModernCallout(
        "Phantom Engaged is the name for that uncertainty bucket: an unavoidable overlap created when privacy "
        "protections break our ability to distinguish silence from disengagement using email metrics alone.",
        W - 2*MARGIN
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "The practical solution is not a clever new metric. It is a classification stance: use intentional actions as "
        "proof of engagement, treat opens as weak evidence, and handle ambiguity conservatively.",
        sNormal
    ))
    
    # -- Section 1 --
    story.append(Paragraph("1. What Changed in Measurement", sH1))
    story.append(Paragraph(
        "The modern inbox is increasingly built to protect recipients from hidden tracking. Apple’s approach is "
        "the most explicit: when a user enables Protect Mail Activity, remote content is privately downloaded in "
        "the background.",
        sNormal
    ))
    
    # Diagram Proof
    story.append(Spacer(1, 12))
    story.append(OverlapDiagram(W - 2*MARGIN))
    story.append(Spacer(1, 12))
    
    # -- Proof of Callout Insertion Capability --
    story.append(Paragraph("2. A Classification Framework (Proof of Callout)", sH1))
    story.append(Paragraph(
        "This is where we would insert your specific callout. Here is what it looks like in this new design:", 
        sNormal
    ))
    
    story.append(Spacer(1, 12))
    story.append(ModernCallout(
        f"<b>Apply this framework to your list.</b> We built a <font color='{TEAL.hexval()}'>free classification tool</font> "
        "to help you map your subscribers into the A/B/C framework described above. There is no opt-in and no paywall.",
        W - 2*MARGIN
    ))
    
    doc.build(story)
    print("Proof PDF generated: Phantom_Engaged_Whitepaper_Proof.pdf")

if __name__ == "__main__":
    build_proof()
