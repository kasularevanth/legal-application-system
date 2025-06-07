




# ============ apps/document_processing/pdf_generator.py ============
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from django.conf import settings
from django.template import Template, Context
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for PDF generation"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceBefore=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=3,
            spaceAfter=12
        ))

    def generate_application_pdf(self, application, return_content=False):
        """Generate PDF for legal application"""
        try:
            # Create filename
            filename = f"{application.application_id}.pdf"
            if return_content:
                from io import BytesIO
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                doc = SimpleDocTemplate(file_path, pagesize=A4)

            # Build PDF content
            story = []
            
            # Header
            story.append(Paragraph(f"Legal Application: {application.template.name}", self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
            
            # Application details
            details_data = [
                ['Application ID:', application.application_id],
                ['Title:', application.title],
                ['Type:', application.template.form_type.title()],
                ['Status:', application.status.replace('_', ' ').title()],
                ['Created:', application.created_at.strftime('%B %d, %Y')],
            ]
            
            if application.submitted_at:
                details_data.append(['Submitted:', application.submitted_at.strftime('%B %d, %Y')])
            
            details_table = Table(details_data, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 20))
            
            # Form data
            story.append(Paragraph("Application Details", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Get template fields for proper labeling
            template_fields = {field.field_name: field for field in application.template.fields.all()}
            
            for field_name, value in application.form_data.items():
                if value:  # Only include non-empty fields
                    field_config = template_fields.get(field_name)
                    label = field_config.label if field_config else field_name.replace('_', ' ').title()
                    
                    story.append(Paragraph(f"{label}:", self.styles['FieldLabel']))
                    
                    # Format value based on field type
                    if isinstance(value, list):
                        formatted_value = ', '.join(str(v) for v in value)
                    elif isinstance(value, dict):
                        formatted_value = json.dumps(value, indent=2)
                    else:
                        formatted_value = str(value)
                    
                    story.append(Paragraph(formatted_value, self.styles['FieldValue']))
            
            # Legal requirements
            if application.template.legal_requirements:
                story.append(Spacer(1, 20))
                story.append(Paragraph("Legal Requirements", self.styles['Heading2']))
                story.append(Paragraph(application.template.legal_requirements, self.styles['Normal']))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            story.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            if return_content:
                pdf_content = buffer.getvalue()
                buffer.close()
                return pdf_content
            else:
                return file_path
                
        except Exception as e:
            logger.error(f"Failed to generate PDF for application {application.application_id}: {e}")
            raise

    def generate_bulk_applications_pdf(self, applications):
        """Generate PDF for multiple applications"""
        filename = f"bulk_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # Title page
        story.append(Paragraph("Legal Applications Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Summary table
        summary_data = [['Application ID', 'Title', 'Status', 'Created Date']]
        for app in applications:
            summary_data.append([
                app.application_id,
                app.title[:30] + '...' if len(app.title) > 30 else app.title,
                app.status.replace('_', ' ').title(),
                app.created_at.strftime('%m/%d/%Y')
            ])
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        doc.build(story)
        
        return file_path