# model/pdf_exports.py

from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import KeepTogether, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .schedule import build_subject_time_slots


def _pdf_path(path: str) -> str:
    return path if path.lower().endswith(".pdf") else f"{path}.pdf"


def _table_style(header_color=colors.lightgrey):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ])


def _detail_table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f1ff")),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#f3f6fa")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c2cc")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfe")]),
    ])


def _p(value, style):
    return Paragraph(escape(str(value or "")), style)


def export_strand_report_pdf(path: str, rows: list):
    doc = SimpleDocTemplate(_pdf_path(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("EduGate - Strand Enrollment Report", styles["Title"]),
        Paragraph(datetime.now().strftime("Generated: %B %d, %Y %I:%M %p"), styles["Normal"]),
        Spacer(1, 12),
    ]

    data = [["Strand", "Daily", "Weekly", "Monthly", "Yearly", "Total"]]
    for row in rows:
        data.append([
            row.get("strand", ""),
            str(row.get("daily", 0)),
            str(row.get("weekly", 0)),
            str(row.get("monthly", 0)),
            str(row.get("yearly", 0)),
            str(row.get("total", 0)),
        ])

    table = Table(data, hAlign="LEFT", repeatRows=1)
    table.setStyle(_table_style())
    story.append(table)
    doc.build(story)


def export_enrollment_report_pdf(path: str, rows: list):
    doc = SimpleDocTemplate(
        _pdf_path(path),
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=26,
        bottomMargin=26,
    )
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        "EnrollmentReportCell",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )
    section_style = ParagraphStyle(
        "EnrollmentReportSection",
        parent=styles["Heading3"],
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#102a43"),
        spaceBefore=6,
        spaceAfter=4,
    )
    story = [
        Paragraph("EduGate - Enrollment Reports Per Student", styles["Title"]),
        Paragraph(datetime.now().strftime("Generated: %B %d, %Y %I:%M %p"), styles["Normal"]),
        Spacer(1, 10),
    ]

    for row in rows:
        name = row.get("full_name") or f"{row.get('last_name', '')}, {row.get('first_name', '')}".strip(", ")
        registrar = "Unknown"
        reg_name = row.get("registrar_name")
        reg_account = row.get("reg_account")
        if reg_name and reg_account:
            registrar = f"{reg_name} ({reg_account})"
        elif reg_name:
            registrar = reg_name

        docs = (
            f"137:{row.get('form_137', '')} | "
            f"138:{row.get('form_138', '')} | "
            f"BC:{row.get('birth_certificate', '')}"
        )
        enrolled_at = row.get("enrolled_at") or ""
        updated_at = row.get("updated_at") or ""

        data = [
            ["Student ID", _p(row.get("student_id", ""), cell_style), "Student Name", _p(name, cell_style)],
            ["Grade / Strand", _p(f"{row.get('grade_level', '')} - {row.get('strand', '')}", cell_style),
             "Section / Schedule", _p(f"{row.get('section', '')} - {row.get('schedule', '')}", cell_style)],
            ["Email", _p(row.get("email", ""), cell_style), "Contact", _p(row.get("contact_number", ""), cell_style)],
            ["Documents", _p(docs, cell_style), "Payment Status", _p(row.get("payment_status", ""), cell_style)],
            ["Registrar", _p(registrar, cell_style), "Enrolled At", _p(enrolled_at, cell_style)],
            ["Status", _p(row.get("status", ""), cell_style), "Last Updated", _p(updated_at, cell_style)],
        ]

        table = Table(data, colWidths=[90, 255, 100, 255], hAlign="LEFT")
        table.setStyle(_detail_table_style())
        story.append(KeepTogether([
            Paragraph(f"{row.get('student_id', '')} - {name}", section_style),
            table,
            Spacer(1, 8),
        ]))

    doc.build(story)


def export_student_receipt_pdf(path: str, student: dict, assignments: dict):
    doc = SimpleDocTemplate(_pdf_path(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("EduGate Enrollment Receipt", styles["Title"]),
        Paragraph(datetime.now().strftime("Generated: %B %d, %Y %I:%M %p"), styles["Normal"]),
        Spacer(1, 12),
    ]

    info = [
        ["Field", "Details"],
        ["ID", student.get("student_id", "")],
        ["Name", student.get("name", "")],
        ["Strand", student.get("strand", "")],
        ["Grade", student.get("grade", "")],
        ["Section", student.get("section", "")],
        ["Schedule", student.get("schedule", "")],
    ]
    info_table = Table(info, colWidths=[100, 350])
    info_table.setStyle(_table_style(colors.lightgrey))
    story.append(info_table)
    story.append(Spacer(1, 18))

    schedule_rows = build_subject_time_slots(
        student.get("schedule", ""),
        student.get("grade", ""),
        student.get("strand", ""),
        assignments,
    )
    time_data = [["Time", "Subject", "Teacher"]]
    for row in schedule_rows:
        time_data.append([row["time"], row["subject"], row["teacher"]])

    story.append(Paragraph("Class Schedule", styles["Heading2"]))
    schedule_table = Table(time_data, colWidths=[120, 220, 140], repeatRows=1)
    schedule_table.setStyle(_table_style(colors.lightgrey))
    story.append(schedule_table)
    doc.build(story)
