# Export Service
# Business logic for data export (CSV and PDF)

from typing import Optional, List, Dict
from datetime import date, datetime
from flask import make_response
from app.models import Student, Attendance, Groups
from app import db
import csv
import io


class ExportService:
    """Service for exporting data."""
    
    @staticmethod
    def export_attendance_csv(
        group_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> make_response:
        """Export attendance records to CSV.
        
        Args:
            group_id: Filter by group ID (optional)
            start_date: Filter by start date YYYY-MM-DD (optional)
            end_date: Filter by end date YYYY-MM-DD (optional)
        
        Returns:
            Flask response with CSV file attachment
        """
        query = db.session.query(
            Student.full_name, Groups.marking, Attendance.attendance
        ).join(Attendance).join(Groups)
        
        if group_id:
            query = query.filter(Student.group_id == group_id)
        
        if start_date:
            parsed_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance >= parsed_start)
        
        if end_date:
            parsed_end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance <= parsed_end)
        
        results = query.order_by(Attendance.attendance.desc()).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student Name', 'Group', 'Attendance Date'])
        
        for row in results:
            writer.writerow([row[0], row[1], row[2]])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=attendance_export_{date.today()}.csv'
        )
        
        return response
    
    @staticmethod
    def export_attendance_pdf(
        group_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_name: Optional[str] = None
    ) -> make_response:
        """Export attendance records to printable PDF sheet.
        
        Args:
            group_id: Filter by group ID (optional)
            start_date: Filter by start date YYYY-MM-DD (optional)
            end_date: Filter by end date YYYY-MM-DD (optional)
            group_name: Name of the group for the header
        
        Returns:
            Flask response with PDF file attachment
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER
        
        # Query data
        query = db.session.query(
            Student.full_name, Groups.marking, Attendance.attendance
        ).join(Attendance).join(Groups)
        
        if group_id:
            query = query.filter(Student.group_id == group_id)
        
        if start_date:
            parsed_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance >= parsed_start)
        
        if end_date:
            parsed_end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance <= parsed_end)
        
        results = query.order_by(Student.full_name, Attendance.attendance).all()
        
        # Group by student for printable sheet
        student_records: Dict[str, List] = {}
        for row in results:
            name = row[0]
            if name not in student_records:
                student_records[name] = []
            student_records[name].append(row[2])
        
        # Build PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=10*mm,
            leftMargin=10*mm,
            topMargin=10*mm,
            bottomMargin=10*mm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16
        )
        
        # Title
        title = f"Attendance Report - {group_name or 'All Groups'}"
        if start_date and end_date:
            title += f" ({start_date} to {end_date})"
        elif start_date:
            title += f" (from {start_date})"
        elif end_date:
            title += f" (until {end_date})"
        
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 10*mm))
        
        # Create table data
        table_data = [['Student Name', 'Attendance Dates']]
        for name, dates in sorted(student_records.items()):
            dates_str = ', '.join([d.strftime('%Y-%m-%d') for d in sorted(dates)])
            table_data.append([name, dates_str])
        
        if not table_data[1:]:
            table_data.append(['No records found', ''])
        
        # Create table
        table = Table(table_data, colWidths=[120*mm, 150*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=attendance_sheet_{date.today()}.pdf'
        )
        
        return response
