import sqlite3
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


DB_PATH = "data/customer_support.db"
DOCUMENT_DIR = Path("data/documents")

DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

styles = getSampleStyleSheet()


# ============================================================
# GET DOCUMENT RECORDS
# ============================================================

cursor.execute("""
SELECT
    d.document_id,
    d.customer_id,
    d.transaction_id,
    d.appointment_id,
    d.document_type,
    d.file_path,
    c.first_name,
    c.last_name,
    t.transaction_date,
    t.amount,
    t.transaction_type,
    t.description,
    t.payment_method,
    t.status,
    a.appointment_date,
    a.appointment_time,
    a.appointment_type,
    p.provider_name,
    p.specialty,
    p.location
FROM documents d
JOIN customers c
    ON d.customer_id = c.customer_id
LEFT JOIN transactions t
    ON d.transaction_id = t.transaction_id
LEFT JOIN appointments a
    ON d.appointment_id = a.appointment_id
LEFT JOIN providers p
    ON a.provider_id = p.provider_id
ORDER BY d.document_id
""")

documents = cursor.fetchall()

print(f"Documents to generate: {len(documents)}")


# ============================================================
# CREATE PDF DOCUMENTS
# ============================================================

for row in documents:

    (
        document_id,
        customer_id,
        transaction_id,
        appointment_id,
        document_type,
        file_path,
        first_name,
        last_name,
        transaction_date,
        amount,
        transaction_type,
        description,
        payment_method,
        transaction_status,
        appointment_date,
        appointment_time,
        appointment_type,
        provider_name,
        specialty,
        location
    ) = row

    output_path = Path(file_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pdf = SimpleDocTemplate(
        str(output_path),
        pagesize=letter
    )

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    title = document_type.replace(
        "_", " "
    ).title()

    story.append(
        Paragraph(
            "Northstar Health Services",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            title,
            styles["Heading1"]
        )
    )

    story.append(Spacer(1, 18))


    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Customer Information",
            styles["Heading2"]
        )
    )

    customer_data = [
        ["Customer ID", customer_id],
        [
            "Customer Name",
            f"{first_name} {last_name}"
        ]
    ]

    customer_table = Table(
        customer_data,
        colWidths=[150, 300]
    )

    customer_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(customer_table)
    story.append(Spacer(1, 20))


    # --------------------------------------------------------
    # APPOINTMENT INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Appointment Information",
            styles["Heading2"]
        )
    )

    appointment_data = [
        ["Appointment ID", appointment_id],
        ["Date", appointment_date],
        ["Time", appointment_time],
        ["Appointment Type", appointment_type],
        ["Provider", provider_name],
        ["Specialty", specialty],
        ["Location", location]
    ]

    appointment_table = Table(
        appointment_data,
        colWidths=[150, 300]
    )

    appointment_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(appointment_table)
    story.append(Spacer(1, 20))


    # --------------------------------------------------------
    # TRANSACTION INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Transaction Information",
            styles["Heading2"]
        )
    )

    transaction_data = [
        ["Transaction ID", transaction_id],
        ["Transaction Date", transaction_date],
        ["Amount", f"${amount:.2f}"],
        ["Transaction Type", transaction_type],
        ["Description", description],
        ["Payment Method", payment_method],
        ["Status", transaction_status]
    ]

    transaction_table = Table(
        transaction_data,
        colWidths=[150, 300]
    )

    transaction_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(transaction_table)
    story.append(Spacer(1, 20))


    # --------------------------------------------------------
    # DOCUMENT-SPECIFIC TEXT
    # --------------------------------------------------------

    if document_type == "invoice":

        story.append(
            Paragraph(
                "This invoice summarizes the healthcare "
                "service and associated charge.",
                styles["BodyText"]
            )
        )

    elif document_type == "receipt":

        story.append(
            Paragraph(
                "This receipt confirms the recorded "
                "payment transaction.",
                styles["BodyText"]
            )
        )

    elif document_type == "insurance_statement":

        story.append(
            Paragraph(
                "This insurance statement summarizes "
                "the transaction associated with this "
                "healthcare service.",
                styles["BodyText"]
            )
        )

    elif document_type == "appointment_summary":

        story.append(
            Paragraph(
                "This document summarizes the customer's "
                "appointment and related transaction.",
                styles["BodyText"]
            )
        )


    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    story.append(Spacer(1, 30))

    story.append(
        Paragraph(
            f"Document ID: {document_id}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            "Synthetic document created for AI portfolio "
            "demonstration purposes only.",
            styles["BodyText"]
        )
    )


    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    pdf.build(story)

    print(
        f"Created: {output_path}"
    )


conn.close()

print("\nAll synthetic PDF documents generated successfully.")