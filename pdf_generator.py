from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import io
from datetime import datetime
import re

def generate_pdf(title, content, source_url):
    """Generate a PDF document from scraped content"""
    
    # Create a BytesIO buffer to store PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor='black'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor='black'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        textColor='black',
        leading=14
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=TA_LEFT,
        textColor='gray'
    )
    
    # Build the document content
    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Add source info
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_info = f"Source: {source_url}<br/>Generated on: {current_time}"
    story.append(Paragraph(source_info, info_style))
    story.append(Spacer(1, 30))
    
    # Process and add content
    lines = content.split('\n')
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Empty line - end current paragraph if it exists
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                if paragraph_text:
                    # Escape HTML characters
                    paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(paragraph_text, body_style))
                    story.append(Spacer(1, 6))
                current_paragraph = []
            continue
        
        # Check if line looks like a heading (short line, all caps, or starts with numbers/bullets)
        if (len(line) < 100 and 
            (line.isupper() or 
             re.match(r'^[\d\.\-\*\#\+]+\s', line) or
             (len(line.split()) < 10 and not line.endswith('.')))):
            
            # End current paragraph if it exists
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                if paragraph_text:
                    paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(paragraph_text, body_style))
                    story.append(Spacer(1, 6))
                current_paragraph = []
            
            # Add as heading
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, heading_style))
        else:
            # Add to current paragraph
            current_paragraph.append(line)
    
    # Add final paragraph if it exists
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        if paragraph_text:
            paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(paragraph_text, body_style))
    
    # Build PDF
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise Exception(f"Failed to generate PDF: {str(e)}")
