import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_report_pdf(
    json_path: str,
    pdf_path: str,
    font_name: str = "Courier",
    title_font: str = "Courier-Bold",
    include_circuit: bool = True,
    alternate_row_color: bool = True,
):
    # ----------------- Load JSON -----------------
    with open(json_path, "r") as f:
        data = json.load(f)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # ----------------- Styles -----------------
    styles["Title"].fontName = title_font
    styles["Title"].fontSize = 20
    styles["Title"].leading = 24

    styles["Heading1"].fontName = title_font
    styles["Heading1"].fontSize = 16
    styles["Heading1"].leading = 20
    styles["Heading1"].spaceAfter = 10

    styles["Heading2"].fontName = title_font
    styles["Heading2"].fontSize = 14
    styles["Heading2"].leading = 18
    styles["Heading2"].spaceAfter = 8

    styles["Heading3"].fontName = title_font
    styles["Heading3"].fontSize = 12
    styles["Heading3"].leading = 16
    styles["Heading3"].spaceAfter = 6

    styles.add(ParagraphStyle(name="MyHeading4", fontName=title_font, fontSize=11, leading=14, spaceAfter=4))

    styles["Code"].fontName = font_name
    styles["Code"].fontSize = 9
    styles["Code"].leading = 11

    styles.add(ParagraphStyle(name="NormalCourier", fontName=font_name, fontSize=10, leading=12))

    story = []
    story.append(Paragraph("Quantum Simulation Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # ----------------- Flatten Config -----------------
    def flatten_config(d, parent_key=""):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_config(v, new_key))
            else:
                items.append([new_key, v])
        return items

    flat_config = flatten_config(data["config"])
    config_table_data = [["Key", "Value"]] + flat_config

    story.append(Paragraph("Simulation Config", styles["Heading1"]))
    table = Table(config_table_data, colWidths=[250, 250])
    t_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
    )
    if alternate_row_color:
        for i in range(1, len(config_table_data)):
            if i % 2 == 0:
                t_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f0f0f0"))
    table.setStyle(t_style)
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    # ----------------- Circuit -----------------
    if include_circuit:
        story.append(Paragraph("Circuit Text", styles["Heading1"]))
        story.append(Preformatted(data["circuit_text"], styles["Code"]))
        story.append(PageBreak())

    # ----------------- Measurements -----------------
    story.append(Paragraph("Measurements", styles["Heading1"]))
    mapped_ordered = data["measurements"]["mapped_ordered"]

    for shot, shot_data in mapped_ordered.items():
        story.append(Paragraph(shot.capitalize(), styles["Heading2"]))
        story.append(Spacer(1, 6))

        rows = [["Type", "Round", "Qubit", "Coords", "Value"]]

        # ancx and ancz
        for qubit_type in ["ancx", "ancz"]:
            if qubit_type in shot_data:
                rounds = shot_data[qubit_type]
                for rnd in rounds:
                    for q in rnd["ord_qubits"]:
                        rows.append([qubit_type.upper(), rnd["round"], q["qubit"], str(q["coords"]), q["value"]])

        # data
        if "data" in shot_data:
            for q in shot_data["data"]["ord_qubits"]:
                rows.append(["DATA", "", q["qubit"], str(q["coords"]), q["value"]])

        t = Table(rows, colWidths=[50, 40, 50, 100, 50])
        t_style = TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
        if alternate_row_color:
            for i in range(1, len(rows)):
                if i % 2 == 0:
                    t_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f0f0f0"))
        t.setStyle(t_style)
        story.append(t)
        story.append(Spacer(1, 12))
        story.append(PageBreak())

    # ----------------- Build PDF -----------------
    doc.build(story)
    print(f"✅ Simulation PDF generated: {pdf_path}")
