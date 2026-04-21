"""
PDF Download Service

This service provides a common utility for generating PDF files from data.
It can be used across different endpoints to download filtered data as PDF.

Usage:
    from services.pdf_download_service import PDFDownloadService
    
    service = PDFDownloadService()
    pdf_response = service.generate_pdf(
        data=data_list,
        columns=column_definitions,
        title="Report Title",
        filename="report.pdf"
    )
    return pdf_response
"""

from django.http import HttpResponse
from io import BytesIO
from decimal import Decimal
import json
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFDownloadService:
    """Service for generating PDF downloads from data"""
    
    def __init__(self):
        self.REPORTLAB_AVAILABLE = REPORTLAB_AVAILABLE
    
    def generate_pdf(self, data, columns=None, title="Report", filename="report.pdf", 
                     page_size=letter, orientation='portrait', return_bytes=False):
        """
        Generate PDF from data list
        
        Args:
            data: List of dictionaries containing the data
            columns: List of column definitions. Each definition can be:
                - String: Field name (used as both key and header)
                - Dict: {'key': 'field_name', 'header': 'Display Name', 'width': 100}
            title: Title of the report
            filename: Name of the PDF file
            page_size: Page size (letter, A4, etc.)
            orientation: 'portrait' or 'landscape'
            return_bytes: If True, returns bytes instead of HttpResponse
        
        Returns:
            HttpResponse with PDF content (if return_bytes=False) or bytes (if return_bytes=True)
        """
        if not self.REPORTLAB_AVAILABLE:
            return self._generate_fallback_pdf(data, columns, title, filename)
        
        try:
            buffer = BytesIO()
            
            # Calculate available width (with margins)
            margin = 0.5 * inch  # 0.5 inch margins on each side
            if orientation == 'landscape':
                available_width = page_size[1] - (2 * margin)
                available_height = page_size[0] - (2 * margin)
                doc = SimpleDocTemplate(
                    buffer, 
                    pagesize=(page_size[1], page_size[0]),
                    leftMargin=margin,
                    rightMargin=margin,
                    topMargin=margin,
                    bottomMargin=margin
                )
            else:
                available_width = page_size[0] - (2 * margin)
                available_height = page_size[1] - (2 * margin)
                doc = SimpleDocTemplate(
                    buffer, 
                    pagesize=page_size,
                    leftMargin=margin,
                    rightMargin=margin,
                    topMargin=margin,
                    bottomMargin=margin
                )
            
            # Build PDF content
            story = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Add date
            date_style = ParagraphStyle(
                'CustomDate',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                alignment=1  # Center alignment
            )
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
            story.append(Spacer(1, 0.3*inch))
            
            if not data or len(data) == 0:
                story.append(Paragraph("No data available", styles['Normal']))
            else:
                # Prepare columns
                if columns is None:
                    # Auto-detect columns from first row
                    if data and len(data) > 0:
                        columns = [{'key': key, 'header': key.replace('_', ' ').title()} for key in data[0].keys()]
                    else:
                        columns = []
                
                # Build table data
                table_data = []
                
                # Create bold style for headers
                header_style = ParagraphStyle(
                    'TableHeader',
                    parent=styles['Normal'],
                    fontSize=9,
                    fontName='Helvetica-Bold',
                    textColor=colors.whitesmoke,
                    alignment=1  # Center alignment
                )
                
                # Add header row with Paragraph for word wrapping
                headers = []
                for col in columns:
                    if isinstance(col, dict):
                        header_text = col.get('header', col.get('key', ''))
                    else:
                        header_text = str(col).replace('_', ' ').title()
                    # Use Paragraph for headers to enable word wrapping
                    header_para = Paragraph(header_text, header_style)
                    headers.append(header_para)
                table_data.append(headers)
                
                # Add data rows with word wrapping
                for row in data:
                    data_row = []
                    for col in columns:
                        if isinstance(col, dict):
                            key = col.get('key', '')
                        else:
                            key = str(col)
                        
                        value = row.get(key, '')
                        # Format value
                        formatted_value = self._format_value(value)
                        # Create a style for data cells with smaller font
                        data_style = ParagraphStyle(
                            'TableData',
                            parent=styles['Normal'],
                            fontSize=8,
                            fontName='Helvetica',
                            textColor=colors.black,
                            alignment=0  # Left alignment
                        )
                        # Wrap long text to prevent overflow
                        wrapped_value = Paragraph(
                            str(formatted_value)[:200],  # Limit to 200 chars
                            data_style
                        )
                        data_row.append(wrapped_value)
                    table_data.append(data_row)
                
                # Calculate column widths
                num_columns = len(columns)
                if num_columns > 0:
                    # Calculate base column width
                    base_col_width = available_width / num_columns
                    # Set minimum and maximum column widths
                    min_col_width = 0.8 * inch
                    max_col_width = 2.5 * inch
                    
                    # Adjust column widths based on content type
                    col_widths = []
                    for col in columns:
                        col_key = col.get('key', '') if isinstance(col, dict) else str(col)
                        # Set width based on column type
                        if 'id' in col_key.lower():
                            col_width = min(0.6 * inch, base_col_width)
                        elif 'name' in col_key.lower() or 'agent' in col_key.lower():
                            col_width = min(max_col_width, max(min_col_width, base_col_width * 1.3))
                        elif 'amount' in col_key.lower() or 'revenue' in col_key.lower() or 'paid' in col_key.lower():
                            col_width = min(max_col_width, max(min_col_width, base_col_width * 1.2))
                        elif 'date' in col_key.lower() or 'created' in col_key.lower():
                            col_width = min(1.2 * inch, max(min_col_width, base_col_width))
                        elif 'status' in col_key.lower():
                            col_width = min(1.0 * inch, max(min_col_width, base_col_width))
                        else:
                            col_width = min(max_col_width, max(min_col_width, base_col_width))
                        
                        col_widths.append(col_width)
                    
                    # Normalize widths to fit available width
                    total_width = sum(col_widths)
                    if total_width > available_width:
                        # Scale down proportionally
                        scale_factor = available_width / total_width
                        col_widths = [w * scale_factor for w in col_widths]
                    elif total_width < available_width * 0.9:
                        # Distribute extra space evenly
                        extra_space = (available_width - total_width) / num_columns
                        col_widths = [w + extra_space for w in col_widths]
                else:
                    col_widths = None
                
                # Create table with calculated column widths
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                
                # Style the table
                table_style = TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center align headers
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),    # Left align data
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),  # Reduced font size
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    
                    # Data rows
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),  # Reduced font size
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
                ])
                
                table.setStyle(table_style)
                story.append(table)
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            # Return bytes if requested (for S3 upload)
            if return_bytes:
                return pdf_content
            
            # Create HTTP response
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            # Fallback to simple PDF or error response
            return self._generate_error_response(str(e), filename)
    
    def _format_value(self, value):
        """Format value for display in PDF"""
        if value is None:
            return ''
        elif isinstance(value, Decimal):
            return f"{value:,.2f}"
        elif isinstance(value, (int, float)):
            return f"{value:,.2f}" if isinstance(value, float) else str(value)
        elif isinstance(value, bool):
            return 'Yes' if value else 'No'
        elif isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        else:
            return str(value)
    
    def _generate_fallback_pdf(self, data, columns, title, filename):
        """Generate a simple text-based response if reportlab is not available"""
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename.replace(".pdf", ".txt")}"'
        
        lines = [title, "=" * len(title), ""]
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        if data and len(data) > 0:
            # Print headers
            if columns:
                headers = []
                for col in columns:
                    if isinstance(col, dict):
                        headers.append(col.get('header', col.get('key', '')))
                    else:
                        headers.append(str(col).replace('_', ' ').title())
                lines.append("\t".join(headers))
                lines.append("-" * 80)
            else:
                # Auto-detect from first row
                headers = list(data[0].keys())
                lines.append("\t".join(headers))
                lines.append("-" * 80)
            
            # Print data
            for row in data:
                values = []
                if columns:
                    for col in columns:
                        if isinstance(col, dict):
                            key = col.get('key', '')
                        else:
                            key = str(col)
                        values.append(str(row.get(key, '')))
                else:
                    values = [str(v) for v in row.values()]
                lines.append("\t".join(values))
        else:
            lines.append("No data available")
        
        response.write("\n".join(lines))
        return response
    
    def _generate_error_response(self, error_message, filename):
        """Generate error response"""
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="error_{filename.replace(".pdf", ".txt")}"'
        response.write(f"Error generating PDF: {error_message}\n\nPlease install reportlab: pip install reportlab")
        return response

