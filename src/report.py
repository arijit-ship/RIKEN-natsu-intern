"""
Generate PDF reports.
PDF related seetings are read from ../setingg/pdf.ini
"""

import configparser
import json
import re
from io import StringIO
from pathlib import Path

from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle
from svglib.svglib import svg2rlg

# ----------------- Hardcoded config path -----------------
PDF_CONFIG_PATH = Path(__file__).resolve().parent.parent / "settings" / "pdf.ini"


# ----------------- Helpers -----------------
def load_pdf_config():
    """Load PDF export settings from ../settings/pdf.ini"""
    config = configparser.ConfigParser()
    config.read(PDF_CONFIG_PATH)
    return config


def parse_color(value: str):
    """Convert string from ini to ReportLab color (#RRGGBB).
    Supports #RGB, #RRGGBB, #RRGGBBAA (drops alpha).
    Raises ValueError if invalid.
    """
    if not value:
        raise ValueError("Color not set in pdf.ini")

    value = value.strip()
    if not value.startswith("#"):
        value = "#" + value

    match = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", value)
    if not match:
        raise ValueError(f"Invalid color format: {value}")

    hex_code = match.group(1)

    # Expand #RGB → #RRGGBB
    if len(hex_code) == 3:
        hex_code = "".join(ch * 2 for ch in hex_code)

    # Strip alpha if present (#RRGGBBAA → #RRGGBB)
    if len(hex_code) == 8:
        hex_code = hex_code[:6]

    return colors.HexColor(f"#{hex_code}")


def safe_getboolean(cfg, section, key, default=False):
    """Return a boolean from ini, fallback to default if invalid."""
    try:
        return cfg.getboolean(section, key, fallback=default)
    except ValueError:
        print(f"Warning: Invalid boolean value for [{section}] {key}, using default={default}")
        return default


def add_page_number(canvas: canvas.Canvas, doc, cfg):
    """Draw page numbers if enabled in config."""
    if safe_getboolean(cfg, "options", "add_page_numbers", False):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(
            doc.pagesize[0] - cfg["page"].getint("margin_right", 40),
            cfg["page"].getint("margin_bottom", 50) / 2,
            text,
        )


# ----------------- Main Function -----------------
def generate_report_pdf(
    json_path: str,
    pdf_path: str,
    svg_str: str | None = None,
):
    """
    Generate a PDF report from the JSON output of the simulator.
    All PDF settings (fonts, colors, sizes, margins, options) are read from ../settings/pdf.ini
    """
    # ----------------- Load Config -----------------
    cfg = load_pdf_config()

    # Fonts & sizes
    font_name = cfg["fonts"].get("normal", "Helvetica")
    title_font = cfg["fonts"].get("title", "Helvetica-Bold")

    title_size = cfg["sizes"].getint("title", 20)
    h1_size = cfg["sizes"].getint("heading1", 16)
    h2_size = cfg["sizes"].getint("heading2", 14)
    h3_size = cfg["sizes"].getint("heading3", 12)
    code_size = cfg["sizes"].getint("code", 9)

    # Colors (from config only, validated)
    header_bg = parse_color(cfg["colors"].get("header_bg", "#d3d3d3"))
    row_alt_bg = parse_color(cfg["colors"].get("row_alt_bg", "#f0f0f0"))

    # Options (safe boolean)
    include_circuit = safe_getboolean(cfg, "options", "include_circuit", False)
    alternate_row_color = safe_getboolean(cfg, "options", "alternate_row_color", False)
    add_page_numbers = safe_getboolean(cfg, "options", "add_page_numbers", False)

    # Page setup
    page_size_name = cfg["page"].get("size", "A4").upper()
    page_size = A4 if page_size_name == "A4" else LETTER
    margins = {
        "left": cfg["page"].getint("margin_left", 40),
        "right": cfg["page"].getint("margin_right", 40),
        "top": cfg["page"].getint("margin_top", 50),
        "bottom": cfg["page"].getint("margin_bottom", 50),
    }

    # ----------------- Load JSON -----------------
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=page_size,
        leftMargin=margins["left"],
        rightMargin=margins["right"],
        topMargin=margins["top"],
        bottomMargin=margins["bottom"],
    )
    styles = getSampleStyleSheet()

    # ----------------- Styles -----------------
    styles["Title"].fontName = title_font
    styles["Title"].fontSize = title_size
    styles["Title"].leading = title_size + 4

    styles["Heading1"].fontName = title_font
    styles["Heading1"].fontSize = h1_size
    styles["Heading1"].leading = h1_size + 4
    styles["Heading1"].spaceAfter = 10

    styles["Heading2"].fontName = title_font
    styles["Heading2"].fontSize = h2_size
    styles["Heading2"].leading = h2_size + 4
    styles["Heading2"].spaceAfter = 8

    styles["Heading3"].fontName = title_font
    styles["Heading3"].fontSize = h3_size
    styles["Heading3"].leading = h3_size + 4
    styles["Heading3"].spaceAfter = 6

    styles.add(ParagraphStyle(name="MyHeading4", fontName=title_font, fontSize=11, leading=14, spaceAfter=4))
    styles["Code"].fontName = font_name
    styles["Code"].fontSize = code_size
    styles["Code"].leading = code_size + 2
    styles.add(ParagraphStyle(name="NormalCourier", fontName=font_name, fontSize=10, leading=12))

    story = []

    # ----------------- Title -----------------
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
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
    )
    if alternate_row_color:
        for i in range(1, len(config_table_data)):
            if i % 2 == 0:
                t_style.add("BACKGROUND", (0, i), (-1, i), row_alt_bg)
    table.setStyle(t_style)
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    # ----------------- Circuit Text -----------------
    if include_circuit and data.get("circuit_text"):
        story.append(Paragraph("Circuit Text", styles["Heading1"]))
        story.append(Preformatted(data["circuit_text"], styles["Code"]))
        story.append(PageBreak())

    # ----------------- SVG Diagram (Circuit Diagram) -----------------
    if include_circuit and svg_str:
        story.append(Paragraph("Circuit Diagram", styles["Heading1"]))
        svg_str = svg_str.replace("lightgray", "#d3d3d3")
        svg_io = StringIO(svg_str)
        drawing: Drawing = svg2rlg(svg_io)

        # Scale to fit page width/height
        page_width = page_size[0] - margins["left"] - margins["right"]
        page_height = page_size[1] - margins["top"] - margins["bottom"]
        scale_w = page_width / drawing.width
        scale_h = page_height / drawing.height
        scale = min(scale_w, scale_h)

        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)

        story.append(drawing)
        story.append(PageBreak())

    # ----------------- Measurements -----------------
    story.append(Paragraph("Measurements", styles["Heading1"]))
    mapped_ordered = data.get("measurements", {}).get("mapped_ordered", {})

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
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
        if alternate_row_color:
            for i in range(1, len(rows)):
                if i % 2 == 0:
                    t_style.add("BACKGROUND", (0, i), (-1, i), row_alt_bg)
        t.setStyle(t_style)
        story.append(t)
        story.append(Spacer(1, 12))
        story.append(PageBreak())

    # ----------------- Build PDF -----------------
    doc.build(
        story,
        onFirstPage=lambda c, d: add_page_number(c, d, cfg) if add_page_numbers else None,
        onLaterPages=lambda c, d: add_page_number(c, d, cfg) if add_page_numbers else None,
    )
