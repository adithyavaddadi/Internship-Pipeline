from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

from src.utils.logger import log_pdf, log_success

def create_resume_pdf(content: str, job: dict, path: str) -> None:
    """Generates an ATS-optimized styled resume PDF using ReportLab."""
    log_pdf(f"Creating ATS tailored resume PDF at: {path}...")
    
    doc = SimpleDocTemplate(
        path, 
        pagesize=A4,
        rightMargin=0.6*inch, 
        leftMargin=0.6*inch,
        topMargin=0.55*inch, 
        bottomMargin=0.55*inch
    )

    navy = colors.HexColor("#0d2b5c")
    dark = colors.HexColor("#191919")
    gray = colors.HexColor("#505050")
    story = []

    # Header section
    story.append(Paragraph(
        "ADITHYA VADDADI",
        ParagraphStyle("N", fontSize=18, fontName="Helvetica-Bold", textColor=navy, alignment=TA_CENTER, spaceAfter=2)
    ))
    story.append(Paragraph(
        "Hyderabad | adithyaadi104@gmail.com | +91-7075615349 | "
        "linkedin.com/in/adithya-vaddadi-536176330 | github.com/adithyavaddadi",
        ParagraphStyle("C", fontSize=8.5, fontName="Helvetica", textColor=gray, alignment=TA_CENTER, spaceAfter=5)
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=navy, spaceAfter=3))
    
    # Subheading
    story.append(Paragraph(
        f"Tailored for: {job.get('title', '')} at {job.get('company', '')} [{job.get('source', '')}] | {job.get('location', '')}",
        ParagraphStyle("T", fontSize=7.5, fontName="Helvetica-Oblique", textColor=gray, alignment=TA_CENTER, spaceAfter=7)
    ))

    # Core styles
    bod = ParagraphStyle("B", fontSize=9, fontName="Helvetica", textColor=dark, spaceAfter=2, leading=13)
    bul = ParagraphStyle("U", fontSize=9, fontName="Helvetica", textColor=dark, spaceAfter=1, leftIndent=10, leading=13)
    sec = ParagraphStyle("S", fontSize=10, fontName="Helvetica-Bold", textColor=dark, spaceBefore=7, spaceAfter=2)

    # Dynamic sections parsing
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 2))
        elif line.isupper() or (line.endswith(":") and len(line) < 45):
            story.append(Paragraph(line.rstrip(":"), sec))
            story.append(HRFlowable(
                width="100%", thickness=0.4, color=colors.HexColor("#cccccc"), spaceAfter=2
            ))
        elif line.startswith(("•", "-", "*")):
            story.append(Paragraph("• " + line.lstrip("•-* "), bul))
        else:
            story.append(Paragraph(line, bod))

    # Appending Static Education (Adithya's real degrees)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceAfter=3))
    story.append(Paragraph("EDUCATION", sec))
    story.append(HRFlowable(
        width="100%", thickness=0.4, color=colors.HexColor("#cccccc"), spaceAfter=2
    ))
    story.append(Paragraph("<b>B.Tech - Artificial Intelligence & Machine Learning</b> | May 2027", bod))
    story.append(Paragraph("Sphoorthy Engineering College, Hyderabad | CGPA: 7.4/10", bod))

    doc.build(story)
    log_success(f"ATS Tailored Resume saved: {path}")


def create_cover_letter_pdf(cover_text: str, job: dict, path: str) -> None:
    """Generates a professional cover letter PDF using ReportLab."""
    log_pdf(f"Creating customized cover letter PDF at: {path}...")
    
    doc = SimpleDocTemplate(
        path, 
        pagesize=A4,
        rightMargin=inch, 
        leftMargin=inch, 
        topMargin=inch, 
        bottomMargin=inch
    )

    navy = colors.HexColor("#0d2b5c")
    dark = colors.HexColor("#191919")
    gray = colors.HexColor("#666666")
    story = []

    # Sender Info
    story.append(Paragraph(
        "ADITHYA VADDADI",
        ParagraphStyle("H", fontSize=16, fontName="Helvetica-Bold", textColor=navy, spaceAfter=2)
    ))
    story.append(Paragraph(
        "adithyaadi104@gmail.com | +91-7075615349 | Hyderabad",
        ParagraphStyle("S", fontSize=9, fontName="Helvetica", textColor=gray, spaceAfter=12)
    ))
    story.append(HRFlowable(width="100%", thickness=1.2, color=navy, spaceAfter=12))
    
    # Recipient Job Header
    story.append(Paragraph(
        f"<b>Re: {job.get('title', '')} — {job.get('company', '')} [{job.get('source', '')}]</b>",
        ParagraphStyle("R", fontSize=10, fontName="Helvetica-Bold", textColor=dark, spaceAfter=12)
    ))

    # Body paragraphs
    body_s = ParagraphStyle("B", fontSize=10, fontName="Helvetica", textColor=dark, leading=16, spaceAfter=8)
    for para in cover_text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_s))

    doc.build(story)
    log_success(f"Cover letter PDF saved: {path}")
