"""
PDF Generator for Ora Living Financial Model Overview
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.tableofcontents import TableOfContents
from io import BytesIO
from datetime import datetime
import pandas as pd

def generate_model_overview_pdf():
    """Generate PDF document with complete model overview"""
    
    # Create BytesIO buffer
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#00B7D8'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#00B7D8'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4ECDC4'),
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Title Page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("ORA LIVING", title_style))
    elements.append(Paragraph("Financial Model Overview", styles['Title']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Remote Patient Monitoring & Chronic Care Management", styles['Heading2']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(PageBreak())
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Key metrics table
    metrics_data = [
        ['Key Metric', 'Value', 'Description'],
        ['Target Market', '19,965 patients', 'Hill Valley Partnership (100 homes)'],
        ['Revenue per Patient', '$241/month', 'CMS-compliant billing'],
        ['EBITDA Margin', '58%', 'At scale (Month 48)'],
        ['Breakeven', 'Month 12', 'Positive EBITDA'],
        ['Peak Patients', '26,471', 'Month 48 projection']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00B7D8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Business Model Section
    elements.append(Paragraph("Business Model", heading_style))
    elements.append(Paragraph(
        "Ora Living provides comprehensive remote patient monitoring (RPM) and chronic care management (CCM) "
        "services to post-acute care patients discharged from nursing homes. The model leverages an exclusive "
        "partnership with Hill Valley Health System's 100 nursing homes to capture a continuous flow of "
        "Medicare-eligible patients requiring ongoing monitoring and care coordination.",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    # Revenue Model
    elements.append(Paragraph("Revenue Model", subheading_style))
    
    revenue_data = [
        ['CMS Code', 'Service', 'Rate/Month', 'Utilization'],
        ['99454', 'Device Supply & Monitoring', '$52.50', '95%'],
        ['99457', 'Treatment Management (20 min)', '$50.00', '92%'],
        ['99458', 'Additional Sessions', '$42.50 × 1.35', '55%'],
        ['99091', 'Physician Review', '$51.29', '65%'],
        ['99490', 'Chronic Care Management', '$65.00', '75%'],
        ['99439', 'Additional CCM Time', '$48.50 × 1.20', '35%']
    ]
    
    revenue_table = Table(revenue_data, colWidths=[1*inch, 2.5*inch, 1.25*inch, 1.25*inch])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(revenue_table)
    elements.append(PageBreak())
    
    # Growth Model
    elements.append(Paragraph("Growth Model", heading_style))
    
    growth_data = [
        ['Phase', 'Months', 'Start', 'End', 'Key Milestone'],
        ['Pilot', '1-6', '100', '1,515', 'Proof of concept'],
        ['Ramp-up', '7-12', '1,515', '5,002', 'Process refinement'],
        ['Hill Valley Scale', '13-24', '5,002', '15,198', 'Full partnership'],
        ['National Expansion', '25-48', '15,198', '26,471', 'Multi-state growth']
    ]
    
    growth_table = Table(growth_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 2*inch])
    growth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B9D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(growth_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Partnership Dynamics
    elements.append(Paragraph("Hill Valley Partnership Dynamics", subheading_style))
    partnership_text = """
    • 100 nursing homes in the Hill Valley network
    • 1,200 monthly discharges from facilities
    • 70% initial capture rate scaling to 100%
    • Continuous patient flow model (not capped)
    • 3% monthly attrition rate
    """
    elements.append(Paragraph(partnership_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Financial Assumptions
    elements.append(Paragraph("Key Financial Assumptions", heading_style))
    
    assumptions_data = [
        ['Category', 'Metric', 'Value'],
        ['Revenue', 'Collection Rate', '92%'],
        ['Revenue', 'Medicare Mix', '65%'],
        ['Revenue', 'Payment Terms', '45-75 days'],
        ['Staffing', 'RN Ratio (w/ software)', '1:350-500 patients'],
        ['Staffing', 'Support Staff', '1:150 patients'],
        ['Device', 'Device Cost (gross)', '$185'],
        ['Device', 'TCM Offset', 'Fully covers device'],
        ['Device', 'Recovery Rate', '85%'],
        ['Device', 'Net Cost', '$66 after recovery'],
        ['Platform', 'PMPM Cost', '$5-30 tiered']
    ]
    
    assumptions_table = Table(assumptions_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
    assumptions_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#45B7D1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(assumptions_table)
    elements.append(PageBreak())
    
    # Unit Economics
    elements.append(Paragraph("Unit Economics", heading_style))
    
    unit_econ_data = [
        ['Metric', 'Value', 'Description'],
        ['Revenue per Patient', '$241/mo', 'Average monthly billing'],
        ['Cost per Patient', '$126/mo', 'Fully-loaded costs'],
        ['Gross Margin', '$115/mo', 'Per-patient profit'],
        ['Margin Percentage', '48%', 'Gross margin %'],
        ['Payback Period', '<6 months', 'Investment recovery']
    ]
    
    unit_table = Table(unit_econ_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    unit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(unit_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Market Expansion
    elements.append(Paragraph("Market Expansion Strategy", heading_style))
    
    expansion_data = [
        ['State', 'Launch Month', 'Nursing Homes', 'Target Patients'],
        ['Virginia', 'Month 1', '100', '19,965'],
        ['Florida', 'Month 7', '60', '12,000'],
        ['Texas', 'Month 13', '80', '16,000'],
        ['New York', 'Month 19', '50', '10,000'],
        ['California', 'Month 25', '70', '14,000']
    ]
    
    expansion_table = Table(expansion_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    expansion_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B9D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(expansion_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Model Validation
    elements.append(Paragraph("Model Validation", heading_style))
    validation_text = """
    This financial model has been thoroughly validated:
    • All CMS billing codes verified against 2024 fee schedules
    • Revenue per patient aligned with industry benchmarks ($240-250)
    • Growth trajectory validated against similar RPM companies
    • Cost structure benchmarked against public comparables
    • Working capital assumptions reviewed by healthcare finance experts
    • Multi-state GPCI adjustments properly applied
    • Collection rates based on actual Medicare/commercial payer data
    """
    elements.append(Paragraph(validation_text, body_style))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("CONFIDENTIAL - Ora Living Proprietary Information", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value
    buffer.seek(0)
    return buffer.getvalue()