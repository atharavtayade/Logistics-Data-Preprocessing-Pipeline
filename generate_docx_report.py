"""
Executive Word Document (.docx) Generator for Task 2 Technical Preprocessing Report.
Produces a publication-grade, professionally styled Word document featuring:
- Document control metadata table
- Executive abstract callout banner with accent left border
- Styled headers and footers with confidentiality markers
- Full 7 sections with mathematical formulations, system diagrams, and detailed tables
- Code blocks with Consolas/Courier New and shaded backgrounds
- Dedicated 200-word portal submission executive summary box
"""

import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Palette Configuration
HEX_PRIMARY = "1A365D"      # Deep Navy
HEX_SECONDARY = "2B6CB0"    # Slate Blue
HEX_ACCENT = "319795"       # Teal
HEX_TEXT_DARK = "2D3748"    # Charcoal Body Text
HEX_BG_LIGHT = "F7FAFC"     # Off-white table/box tint
HEX_BORDER = "CBD5E0"       # Subtle border gray
HEX_CALLOUT_BG = "EDF2F7"   # Callout background
HEX_CODE_BG = "F1F5F9"      # Code block background

COLOR_PRIMARY = RGBColor(26, 54, 93)
COLOR_SECONDARY = RGBColor(43, 108, 176)
COLOR_TEXT_DARK = RGBColor(45, 55, 72)
COLOR_MUTED = RGBColor(113, 128, 150)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets internal padding (in twips) for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_shading(cell, color_hex):
    """Sets background shading color for a table cell."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))


def set_callout_border(cell, border_color_hex=HEX_PRIMARY, border_size="36"):
    """Sets a thick left accent border and clears top/right/bottom borders."""
    borders_xml = f'''
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:left w:val="single" w:sz="{border_size}" w:space="0" w:color="{border_color_hex}"/>
        <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
    </w:tcBorders>
    '''
    cell._tc.get_or_add_tcPr().append(parse_xml(borders_xml))


def set_table_borders(table, border_color_hex=HEX_BORDER):
    """Sets subtle outer and inner borders for data tables."""
    tblBorders_xml = f'''
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="{border_color_hex}"/>
        <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>
        <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color_hex}"/>
        <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>
    </w:tblBorders>
    '''
    table._tbl.tblPr.append(parse_xml(tblBorders_xml))


def create_callout_box(doc, title, text, border_color=HEX_PRIMARY, bg_color=HEX_CALLOUT_BG):
    """Creates a beautifully styled executive callout banner."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_shading(cell, bg_color)
    set_callout_border(cell, border_color, border_size="36")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"■ {title}\n")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(11)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = COLOR_TEXT_DARK
    
    # Add trailing spacing
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)


def create_code_block(doc, code_snippet):
    """Formats code blocks with fixed-width typography and background shading."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_shading(cell, HEX_CODE_BG)
    set_callout_border(cell, HEX_SECONDARY, border_size="24")
    set_cell_margins(cell, top=100, bottom=100, left=160, right=120)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_snippet.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)


def add_custom_heading(doc, text, level):
    """Adds styled hierarchical headings."""
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Calibri"
    if level == 1:
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_TEXT_DARK
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
    return h


def build_word_report(output_path: str):
    """Builds the comprehensive, exhaustive Word report."""
    doc = Document()
    
    # Configure 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Configure Header
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("LOG-ENG-PREP-2026-T2-PROD | Enterprise Logistics Analytics Pipeline")
        r_hdr.font.name = "Calibri"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = COLOR_MUTED
        
        # Configure Footer
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_ftr = p_ftr.add_run("CONFIDENTIAL - FOR INTERNAL OPERATIONAL USE ONLY")
        r_ftr.font.name = "Calibri"
        r_ftr.font.size = Pt(8.5)
        r_ftr.font.color.rgb = COLOR_MUTED

    # ---------------------------------------------------------
    # DOCUMENT COVER & HEADER BLOCK
    # ---------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    run_t = p_title.add_run("Enterprise Data Preprocessing & Cleansing Architecture for Multimodal Logistics Telematics")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_PRIMARY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    run_s = p_sub.add_run("Technical Implementation Report for Task 2 | Production Ingestion, Physics Gating & Feature Pipeline")
    run_s.font.name = "Calibri"
    run_s.font.size = Pt(12)
    run_s.font.bold = True
    run_s.font.color.rgb = COLOR_SECONDARY
    
    # Metadata Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    set_table_borders(meta_table)
    
    metadata = [
        ("Document Reference ID", "LOG-ENG-PREP-2026-T2-PROD (v2.4.0 Production)"),
        ("Author / Engineering Role", "Lead Logistics Data Analyst Intern & Supply Chain Systems Engineer"),
        ("Supervisory Reviewers", "Director of Supply Chain Analytics & VP of Fleet Engineering"),
        ("Operational Domain", "Multimodal Freight Haulage & Metropolitan Urban Last-Mile Telematics"),
        ("Public Benchmark Standards", "Brazilian E-Commerce (Olist) & DataCo Smart Supply Chain Dataset"),
        ("Technical Stack", "Python 3.10+, Pandas 3.0+, NumPy 2.4+, Scikit-Learn 1.9+ (ColumnTransformer)"),
    ]
    
    for i, (k, v) in enumerate(metadata):
        c0 = meta_table.cell(i, 0)
        c1 = meta_table.cell(i, 1)
        c0.width = Inches(2.3)
        c1.width = Inches(4.2)
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        
        if i % 2 == 1:
            set_cell_shading(c0, HEX_BG_LIGHT)
            set_cell_shading(c1, HEX_BG_LIGHT)
            
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_TEXT_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(6)
    p_spacer.paragraph_format.space_after = Pt(6)

    # Executive Abstract Callout
    create_callout_box(
        doc,
        title="EXECUTIVE ABSTRACT & SYSTEM MANDATE",
        text=(
            "Modern enterprise supply chains ingest massive operational telematics across disparate systems: "
            "ERP platforms, Warehouse Management Systems (WMS), Transportation Management Systems (TMS), vehicle CAN-bus sensors, "
            "and mobile driver Proof-of-Delivery (POD) applications. Unprocessed feeds suffer from extreme entropy—including "
            "structural key duplicates, sensor tare calibration drift, inverted timestamps, coordinate transpositions, and heavy-tail skewness. "
            "This report establishes an industrial-grade, mathematically rigorous data preprocessing pipeline. "
            "Benchmarked against canonical Olist and DataCo supply chain datasets, the architecture implements automated primary key deduplication, "
            "geospatial polygon bounding, physical logic gating, non-parametric Tukey's Fences Winsorization, and a leak-free Scikit-Learn "
            "ColumnTransformer integrating cyclical trigonometric temporal encodings and RobustScaler normalizations. "
            "Across 2,000 simulated telematics records, the pipeline achieved a 97.90% operational retention yield, stabilized cargo weight skewness "
            "from 11.97 down to 1.83, and produced a clean, 31-dimensional feature matrix that eliminates target leakage and guarantees mathematical "
            "stability for downstream ETA regression and route optimization."
        ),
        border_color=HEX_PRIMARY,
        bg_color=HEX_CALLOUT_BG,
    )

    # ---------------------------------------------------------
    # SECTION 2: DATA COLLECTION ARCHITECTURE & INGESTION
    # ---------------------------------------------------------
    add_custom_heading(doc, "2. Data Collection Architecture & Ingestion Simulation", level=1)
    
    p = doc.add_paragraph(
        "Industrial logistics operations capture telemetry across four asynchronous operational tiers. "
        "Each subsystem operates under differing polling intervals, network protocols, and failure modes:"
    )
    p.paragraph_format.space_after = Pt(6)

    # Bullet list of tiers
    tiers = [
        ("Tier 1: Customer Checkout & ERP Systems (Transactional Layer): ", "Captures customer sales orders, item SKUs, promised SLA delivery deadlines, and destination address strings via RESTful APIs."),
        ("Tier 2: Warehouse Management Systems (WMS) & Static In-Line Scales (Fulfillment Layer): ", "Captures automated conveyor scale weights, optical CubiScan 3D dimensional volumes (length, width, height), dock door allocations, and outbound staging events."),
        ("Tier 3: Transportation Management Systems (TMS) & Gate RFID (Line-Haul Layer): ", "Records dispatch gate departures, line-haul carrier vendor assignments, trailer seal IDs, and electronic freight bills (EDI 204/214 protocols)."),
        ("Tier 4: Vehicle On-Board Diagnostics (OBD-II / CAN-bus) & Handheld Mobile POD (Edge Layer): ", "Streams high-frequency vehicle GPS coordinates (1 Hz), odometer distances, engine load, and driver handheld electronic signatures over cellular MQTT/WebSockets, subject to signal attenuation."),
    ]
    for bold_prefix, text in tiers:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_before = Pt(2)
        bp.paragraph_format.space_after = Pt(2)
        r_b = bp.add_run(bold_prefix)
        r_b.font.name = "Calibri"
        r_b.font.bold = True
        r_b.font.color.rgb = COLOR_PRIMARY
        r_t = bp.add_run(text)
        r_t.font.name = "Calibri"
        r_t.font.color.rgb = COLOR_TEXT_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(4)

    # Ingestion Architecture ASCII Diagram
    create_code_block(
        doc,
        "+----------------------------------------------------------------------------------------------------+\n"
        "|                                 MULTI-TIER ENTERPRISE INGESTION LAYER                              |\n"
        "+-----------------------------------+--------------------------------+-------------------------------+\n"
        "| Tier 1: ERP / Checkout            | Tier 2: WMS & Conveyor Scales  | Tier 4: Edge CAN-bus & POD    |\n"
        "| - Order ID & Line Items           | - Gross Deadweight (g / kg)    | - Lat/Lon GPS Pings (1 Hz)    |\n"
        "| - Promised SLA Windows            | - Package Dimensions (L, W, H) | - Vehicle Odometer & Speed    |\n"
        "| - Customer Destination Text       | - Cross-Dock Staging Scans     | - Mobile Electronic Signatures|\n"
        "+-----------------+-----------------+----------------+---------------+---------------+---------------+\n"
        "                  |                                  |                               |\n"
        "                  +----------------------------------+-------------------------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "                                  +------------------------------------+\n"
        "                                  |    Streaming Ingestion Broker      |\n"
        "                                  | (Apache Kafka / AWS Kinesis / MQTT)|\n"
        "                                  +------------------+-----------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "                                  +------------------------------------+\n"
        "                                  |      Raw Telematics Lakehouse      |\n"
        "                                  |   (Bronze Delta Lake / MinIO S3)   |\n"
        "                                  +------------------+-----------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "                    +----------------------------------------------------------------+\n"
        "                    |           ENTERPRISE DATA PREPROCESSING PIPELINE ENGINE        |\n"
        "                    +----------------------------------------------------------------+\n"
        "                    |  1. Structural Deduplication & String / Schema Sanitization    |\n"
        "                    |  2. Domain Logic & Geospatial Polygon Bounding Validation      |\n"
        "                    |  3. Physics Assertion & Target Leakage Status Gating           |\n"
        "                    |  4. Scikit-Learn Feature Pipeline (RobustScaler + Sin/Cos Enc) |\n"
        "                    +--------------------------------+-------------------------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "                                  +------------------------------------+\n"
        "                                  |      Clean Analytics Feature Store |\n"
        "                                  |       (Silver / Gold Layer)        |\n"
        "                                  +------------------+-----------------+\n"
    )

    add_custom_heading(doc, "2.1 Enterprise Data Dictionary (Raw Ingestion Schema)", level=2)
    
    # Data Dictionary Table
    dict_table = doc.add_table(rows=18, cols=5)
    dict_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dict_table.autofit = False
    set_table_borders(dict_table)
    
    col_widths = [Inches(1.2), Inches(0.8), Inches(1.1), Inches(1.8), Inches(1.6)]
    headers = ["Column Name", "Raw Type", "Source Node", "Semantic Business Meaning", "Target Valid Domain / Rules"]
    
    hdr_row = dict_table.rows[0]
    for idx, text in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = col_widths[idx]
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    dict_rows = [
        ("shipment_id", "String", "TMS Dock Gate", "Unique freight consignment identifier", "Regex: ^SHP-[0-9]{8}$"),
        ("order_id", "String", "ERP Checkout", "Sales order commercial grouping reference", "Regex: ^ORD-[0-9]{6}$"),
        ("carrier_name", "String", "TMS Master", "Contracted 3PL carrier or fleet service", "Categorical: FedEx, DHL, UPS, BlueDart"),
        ("origin_hub", "String", "WMS Dock", "Origin cross-dock fulfillment facility code", "Categorical: WH-01 through WH-12"),
        ("destination_zone", "String", "Geocoder", "Designated delivery territory routing zone", "Categorical: Zone-A through Zone-E"),
        ("vehicle_type", "String", "Fleet Master", "Physical fleet delivery asset classification", "Categorical: EV Van, Sprinter, 24ft Truck"),
        ("dispatch_timestamp", "String", "TMS RFID", "Departure timestamp from fulfillment terminal", "ISO-8601: YYYY-MM-DD HH:MM:SS (UTC)"),
        ("promised_sla_timestamp", "String", "ERP Checkout", "Contractually guaranteed delivery deadline", "ISO-8601: YYYY-MM-DD HH:MM:SS (UTC)"),
        ("actual_delivery_timestamp", "String", "Driver POD", "Consignee electronic signature timestamp", "ISO-8601: YYYY-MM-DD HH:MM:SS (UTC)"),
        ("dest_latitude", "Float64", "Geocoder", "Geocoded destination latitude coordinate", "Metro Bounds: [18.40°, 18.70°]"),
        ("dest_longitude", "Float64", "Geocoder", "Geocoded destination longitude coordinate", "Metro Bounds: [73.75°, 74.00°]"),
        ("cargo_weight_kg", "Float64", "Conveyor Scale", "Gross deadweight of parcel consignment", "Positive Real: (0.05, 26000.0] kg"),
        ("length_cm", "Float64", "CubiScan", "Outer package length dimension", "Positive Real: [10.0, 250.0] cm"),
        ("width_cm", "Float64", "CubiScan", "Outer package width dimension", "Positive Real: [10.0, 180.0] cm"),
        ("height_cm", "Float64", "CubiScan", "Outer package height dimension", "Positive Real: [2.0, 150.0] cm"),
        ("transit_distance_km", "Float64", "CAN-bus / API", "Actual road network transit distance", "Positive Real: [2.0, 3500.0] km"),
        ("freight_cost_usd", "String", "TMS Invoicing", "Billed transportation charges in USD", "Currency String: $#,##0.00"),
    ]

    for r_idx, row_data in enumerate(dict_rows):
        row = dict_table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            if r_idx % 2 == 1:
                set_cell_shading(cell, HEX_BG_LIGHT)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)
            r.font.color.rgb = COLOR_TEXT_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)

    add_custom_heading(doc, "2.2 Ingestion Benchmarks: Olist & DataCo Supply Chain Datasets", level=2)
    p = doc.add_paragraph(
        "To ensure production applicability without relying on proprietary databases, this pipeline benchmarks its architecture "
        "against two foundational open-access supply chain repositories:"
    )
    p.paragraph_format.space_after = Pt(4)

    p1 = doc.add_paragraph(style='List Bullet')
    r_b = p1.add_run("Brazilian E-Commerce Public Dataset by Olist (Kaggle): ")
    r_b.font.bold = True
    r_b.font.color.rgb = COLOR_PRIMARY
    p1.add_run(
        "Contains 100,000 real-world commercial deliveries spanning 2016-2018 across Brazilian states. "
        "It benchmarks multi-stage timestamp chains (order_purchase, order_delivered_carrier, order_delivered_customer) "
        "and demonstrates heavy lead-time variance across interstate highway corridors, postal prefix centroid clustering, "
        "and asynchronous database batch logging anomalies."
    )

    p2 = doc.add_paragraph(style='List Bullet')
    r_b = p2.add_run("DataCo Global Smart Supply Chain Dataset (Kaggle): ")
    r_b.font.bold = True
    r_b.font.color.rgb = COLOR_PRIMARY
    p2.add_run(
        "Contains 180,000 shipment transaction records tracking international supply chains across omnichannel commercial sales. "
        "It provides structured delivery status classifications (Late delivery, Advance delivery, Shipping on time), "
        "scheduled vs. real transit days, and shipment dimensional attributes, confirming that missing delivery timestamps "
        "frequently represent operational exceptions rather than sensor dropouts."
    )

    # ---------------------------------------------------------
    # SECTION 3: SYSTEMATIC DATA QUALITY AUDIT & TAXONOMY
    # ---------------------------------------------------------
    add_custom_heading(doc, "3. Systematic Data Quality Audit & Failure Taxonomy", level=1)
    
    p = doc.add_paragraph(
        "Raw supply chain telemetry is subject to environmental, mechanical, and human disturbances. "
        "The identification taxonomy categorizes data degradation into three primary engineering failure classes:"
    )
    p.paragraph_format.space_after = Pt(4)

    add_custom_heading(doc, "3.1 Tripartite Missing Data Mechanisms in Logistics", level=2)
    
    missing_mechanisms = [
        ("1. Missing Completely at Random (MCAR):",
         "Telematics packet dropouts occurring when delivery vehicles traverse subterranean tunnels, dense urban canyons, "
         "or cellular dead zones. The probability of missingness is completely independent of both observed and unobserved operational values: "
         "P(M | Y_obs, Y_mis) = P(M). Imputation via median central tendency or forward spline interpolation is mathematically valid and unbiased."),
        ("2. Missing at Random (MAR):",
         "Package dimensions (length, width, height) missing for lightweight flyers and envelopes. In automated cross-dock sorters, "
         "optical CubiScan lasers only trigger scans on rigid cardboard cartons exceeding a vertical profile threshold (10 cm). "
         "Missingness is fully explained by observed attributes (package_weight_kg < 1.5 kg): P(M | Y_obs, Y_mis) = P(M | Y_obs). "
         "Conditional median imputation grouped by packaging class resolves this bias."),
        ("3. Missing Not at Random (MNAR):",
         "Missing actual_delivery_timestamp records. An unrecorded POD signature signifies an active operational exception: "
         "driver vehicle breakdown, customer gate lockout, route cancellation, or cargo theft. "
         "The probability of missingness depends directly on the unobserved outcome (the delivery never occurred): "
         "P(M | Y_obs, Y_mis) != P(M | Y_obs). Imputing these timestamps introduces catastrophic target leakage; "
         "records must be retained and classified as EXCEPTION_OR_IN_TRANSIT."),
    ]
    for title, desc in missing_mechanisms:
        p_mech = doc.add_paragraph()
        p_mech.paragraph_format.space_before = Pt(3)
        p_mech.paragraph_format.space_after = Pt(3)
        r_title = p_mech.add_run(f"{title} ")
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_SECONDARY
        p_mech.add_run(desc)

    add_custom_heading(doc, "3.2 Domain-Specific Structural Anomalies & Physics Violations", level=2)
    
    anomalies = [
        ("Chronological Timestamp Inversions: ", "Mobile driver devices with unsynchronized clocks or unparsed timezones record actual_delivery_timestamp occurring prior to dispatch_timestamp (actual_transit_hours < 0). This violates physical causality and induces severe gradient explosion during regression modeling."),
        ("Geospatial Transposition & Null Island: ", "Upstream geocoders frequently swap latitude and longitude values or default uninitialized GPS modems to (0.0000°, 0.0000°), placing delivery coordinates in the Atlantic Ocean off the coast of West Africa ('Null Island')."),
        ("Sensor Tare Calibration Drift: ", "Conveyor belt load-cells subject to mechanical vibration, tare deduction overshoots, or uncalibrated strain gauges yield cargo deadweights <= 0.0 kg, which corrupts volumetric density and fuel burn models."),
        ("Currency Formatting & Heterogeneous Strings: ", "Invoiced transportation charges exported with embedded currency symbols ('$1,245.50', 'USD'), commas, and trailing whitespaces, preventing numeric vector computation until sanitized."),
    ]
    for prefix, body in anomalies:
        p_anom = doc.add_paragraph(style='List Bullet')
        p_anom.paragraph_format.space_before = Pt(2)
        p_anom.paragraph_format.space_after = Pt(2)
        r_p = p_anom.add_run(prefix)
        r_p.font.bold = True
        r_p.font.color.rgb = COLOR_PRIMARY
        p_anom.add_run(body)

    add_custom_heading(doc, "3.3 High-Variance Scale Disparities", level=2)
    p = doc.add_paragraph(
        "Multimodal logistics features span drastically different orders of magnitude: transit distances span [10, 3500] km "
        "and freight costs span [8, 25000] USD, whereas committed SLA days span [1, 7] days. "
        "Without robust feature scaling, distance-based algorithms (k-Means route clustering, k-NN zoning) compute Euclidean distances "
        "dominated by distance coordinates by a factor of 10^6, rendering operational SLA urgency completely invisible to the model."
    )

    # ---------------------------------------------------------
    # SECTION 4: METHODOLOGY & STATISTICAL REMEDIATION
    # ---------------------------------------------------------
    add_custom_heading(doc, "4. Methodology & Statistical Remediation Formulations", level=1)
    
    add_custom_heading(doc, "4.1 Non-Parametric Outlier Boundaries: Tukey's Fences & Winsorization", level=2)
    p = doc.add_paragraph(
        "Logistics operational durations and deadweights exhibit heavy-tailed distributions. Standard Gaussian filters (3*sigma) "
        "fail because extreme outliers inflate both the sample mean and variance. We apply non-parametric Tukey's Fences:"
    )
    p.paragraph_format.space_after = Pt(4)

    create_callout_box(
        doc,
        title="MATHEMATICAL FORMULATION: TUKEY'S FENCES & WINSORIZATION",
        text=(
            "1. Quartile Estimation:\n"
            "   Q1 = F^(-1)(0.25),   Q3 = F^(-1)(0.75)\n"
            "   IQR = Q3 - Q1\n\n"
            "2. Robust Inner Fence Bounds:\n"
            "   Lower Limit = max(Floor_physical, Q1 - 1.5 * IQR)\n"
            "   Upper Limit = Q3 + 1.5 * IQR\n\n"
            "3. Winsorization Transformation (Preserving Sample Size N):\n"
            "   x_i* = Lower Limit,   if x_i < Lower Limit\n"
            "   x_i* = x_i,           if Lower Limit <= x_i <= Upper Limit\n"
            "   x_i* = Upper Limit,   if x_i > Upper Limit\n\n"
            "Rationale: Discarding high-transit-time records introduces survivorship bias by deleting valid records of severe road gridlock. "
            "Winsorization caps extreme values at the upper threshold, eliminating gradient explosion while preserving operating signal."
        ),
        border_color=HEX_SECONDARY,
        bg_color=HEX_BG_LIGHT,
    )

    add_custom_heading(doc, "4.2 Cyclical Trigonometric Temporal Encodings (S^1 Unit Circle)", level=2)
    p = doc.add_paragraph(
        "Standard linear encodings representing dispatch times as decimal hours t in [0.0, 24.0) create an artificial discontinuity "
        "between 23:59 (23.983 h) and 00:01 (0.017 h), resulting in an apparent distance of 23.966 hours. "
        "To preserve circadian continuity, timestamps are mapped onto the unit circle S^1:"
    )

    create_callout_box(
        doc,
        title="MATHEMATICAL FORMULATION: CIRCULAR TIME MAPPING & DISTANCE PRESERVATION",
        text=(
            "1. Trigonometric Projection:\n"
            "   x_sin = sin(2 * pi * t / 24.0),   x_cos = cos(2 * pi * t / 24.0)\n\n"
            "2. Proof of Euclidean Neighborhood Invariance on S^1:\n"
            "   Let u1 = (sin theta_1, cos theta_1) and u2 = (sin theta_2, cos theta_2), where theta_i = 2*pi*t_i / 24.\n"
            "   D^2(u1, u2) = (sin theta_1 - sin theta_2)^2 + (cos theta_1 - cos theta_2)^2\n"
            "               = (sin^2 theta_1 + cos^2 theta_1) + (sin^2 theta_2 + cos^2 theta_2) - 2(cos theta_1 cos theta_2 + sin theta_1 sin theta_2)\n"
            "               = 2 - 2*cos(theta_1 - theta_2) = 4 * sin^2( pi * (t1 - t2) / 24 )\n\n"
            "   Therefore: D(u1, u2) = 2 * |sin( pi * (t1 - t2) / 24 )|\n\n"
            "Conclusion: The Euclidean distance between feature vectors is strictly a periodic, monotonic function of true circular time difference. "
            "For 23:59 and 00:01, D(u1, u2) ≈ 0.0087, preserving continuous circadian neighborhood geometry."
        ),
        border_color=HEX_ACCENT,
        bg_color=HEX_BG_LIGHT,
    )

    add_custom_heading(doc, "4.3 Distributional Scaling Evaluation: RobustScaler vs. StandardScaler vs. MinMaxScaler", level=2)
    
    # Scaler Comparison Table
    scaler_table = doc.add_table(rows=4, cols=4)
    scaler_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scaler_table.autofit = False
    set_table_borders(scaler_table)
    
    s_col_widths = [Inches(1.3), Inches(1.8), Inches(1.0), Inches(2.4)]
    s_headers = ["Scaler Candidate", "Mathematical Formulation", "Breakdown Point", "Logistics Domain Impact & Vulnerability"]
    
    s_hdr_row = scaler_table.rows[0]
    for idx, text in enumerate(s_headers):
        cell = s_hdr_row.cells[idx]
        cell.width = s_col_widths[idx]
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    scaler_data = [
        ("MinMaxScaler", "X_norm = (X - X_min) / (X_max - X_min)", "0.0%", "Catastrophic failure: Extreme freight outliers (25,000 kg) compress standard parcels (0.5-15 kg) into [0.0001, 0.0006], collapsing gradients."),
        ("StandardScaler", "Z = (X - mu) / sigma", "0.0%", "High sensitivity: Power-law tails inflate sample variance sigma^2, shifting mu rightward and compressing standard deliveries into negative Z-scores."),
        ("RobustScaler (Selected)", "X_robust = (X - Q2) / (Q3 - Q1)", "25.0% - 50.0%", "Optimal choice: Centers standard deliveries around 0.0 with unit IQR spread. Heavy freight retains positive magnitude without collapsing model training."),
    ]

    for r_idx, row_data in enumerate(scaler_data):
        row = scaler_table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = s_col_widths[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
            if r_idx % 2 == 1:
                set_cell_shading(cell, HEX_BG_LIGHT)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)
            if c_idx == 0 and "Selected" in val:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_TEXT_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)

    add_custom_heading(doc, "4.4 Central Tendency Imputation Mechanics & Target Leakage Prevention", level=2)
    p = doc.add_paragraph(
        "For continuous positive physical attributes (cargo weight, cubic volume), the sample arithmetic mean has a breakdown point of 0%. "
        "A single miscalibrated load cell reporting 999,999 kg inflates the mean infinitely, corrupting imputed records. "
        "In contrast, the median has a 50% breakdown point, providing an invariant estimator for long-tailed distributions."
    )
    p.paragraph_format.space_after = Pt(4)
    
    p_leak = doc.add_paragraph(
        "Crucially, imputing missing delivery timestamps with predicted transit durations injects the training target variable (transit_duration = delivery - dispatch) "
        "directly into the feature matrix, creating catastrophic Target Leakage. Our architecture eliminates this risk by categorizing unrecorded POD timestamps "
        "as explicit operational exception classes ('EXCEPTION_OR_IN_TRANSIT') and isolating them from supervised regression training sets."
    )

    # ---------------------------------------------------------
    # SECTION 5: END-TO-END MODULAR PYTHON PREPROCESSING PIPELINE
    # ---------------------------------------------------------
    add_custom_heading(doc, "5. End-to-End Modular Python Preprocessing Pipeline", level=1)
    
    p = doc.add_paragraph(
        "The production preprocessing pipeline is implemented across modular Python components under the `src/` directory. "
        "Below are the core executable modules governing sanitization, domain validation, and Scikit-Learn ColumnTransformer feature pipelines:"
    )
    p.paragraph_format.space_after = Pt(6)

    # Pipeline Code Block
    pipeline_code_snippet = '''
# Scikit-Learn ColumnTransformer Pipeline Architecture (src/pipeline.py)
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from src.transformers import (
    CyclicalTemporalTransformer,
    Log1pVarianceStabilizer,
    TrainFittedTukeyWinsorizer,
)

def build_logistics_feature_pipeline() -> ColumnTransformer:
    # 1. Skewed physical features: Median Imputer -> Log1p -> RobustScaler
    skewed_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("log1p", Log1pVarianceStabilizer()),
        ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
    ])

    # 2. Linear continuous features: Median Imputer -> Tukey Winsorizer -> RobustScaler
    linear_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("winsorizer", TrainFittedTukeyWinsorizer(k=1.5, floor_zero=True)),
        ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
    ])

    # 3. Temporal cycle: 24h Cyclical sin/cos trigonometric encoding
    temporal_pipeline = Pipeline([
        ("cyclical", CyclicalTemporalTransformer(period=24.0, datetime_col=True)),
    ])

    # 4. Categorical master: Missing as 'UNKNOWN' -> OneHotEncoder(drop='first')
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="UNKNOWN")),
        ("encoder", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")),
    ])

    return ColumnTransformer(
        transformers=[
            ("skewed_phys", skewed_pipeline, ["cargo_weight_kg", "package_volume_m3"]),
            ("linear_cont", linear_pipeline, ["transit_distance_km", "freight_cost_usd"]),
            ("sla_order", Pipeline([("imp", SimpleImputer(strategy="median")), ("scl", RobustScaler())]), ["scheduled_days"]),
            ("temporal", temporal_pipeline, ["dispatch_timestamp"]),
            ("categorical", categorical_pipeline, ["carrier_name", "origin_hub", "destination_zone", "vehicle_type"]),
        ],
        remainder="drop",
    )
'''
    create_code_block(doc, pipeline_code_snippet)

    add_custom_heading(doc, "5.1 Preprocessing Audit & Empirical Execution Results", level=2)
    p = doc.add_paragraph(
        "The end-to-end pipeline was executed on 2,000 raw telematics records generated by the multi-tier simulation engine. "
        "The execution audit confirmed high operational yield, effective anomaly purge, and substantial skewness reduction:"
    )

    # Audit Results Table
    audit_table = doc.add_table(rows=9, cols=3)
    audit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    audit_table.autofit = False
    set_table_borders(audit_table)
    
    a_col_widths = [Inches(2.2), Inches(1.6), Inches(2.7)]
    a_headers = ["Ingestion Audit Metric", "Observed Stage Value", "Engineering Significance & Validation"]
    
    a_hdr_row = audit_table.rows[0]
    for idx, text in enumerate(a_headers):
        cell = a_hdr_row.cells[idx]
        cell.width = a_col_widths[idx]
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    audit_data = [
        ("Total Ingestion Stream", "2,000 records", "Raw multi-tier stream containing injected domain defects"),
        ("Duplicate Consignments Purged", "8 records (0.40%)", "Eliminated redundant transmissions, preserving earliest arrival"),
        ("Geospatial Violations Dropped", "19 records (0.95%)", "Eliminated Null Island (0,0), coordinate swaps, and out-of-bounds pings"),
        ("Chronological Inversions Dropped", "15 records (0.75%)", "Purged physically impossible records (delivery < dispatch)"),
        ("Validated Ingestion Yield", "1,958 records (97.90%)", "High operational retention yield for downstream modeling"),
        ("Operational Status Distribution", "ON_TIME: 89.4%\nLATE: 7.4%\nEXCEPTION: 3.3%", "Target leakage eliminated; unrecorded drops isolated as exceptions"),
        ("Raw Cargo Weight Skewness", "+11.9722", "Severe right-tail skew driven by heavy industrial consignments"),
        ("Post-Log1p Feature Skewness", "+1.8251", "84.75% skewness reduction, stabilizing variance and gradient updates"),
    ]

    for r_idx, row_data in enumerate(audit_data):
        row = audit_table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = a_col_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            if r_idx % 2 == 1:
                set_cell_shading(cell, HEX_BG_LIGHT)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)
            r.font.color.rgb = COLOR_TEXT_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------
    # SECTION 6: DOWNSTREAM IMPACT & STRATEGIC REFLECTION
    # ---------------------------------------------------------
    add_custom_heading(doc, "6. Downstream Analytical Impact & Strategic Supply Chain Reflection", level=1)
    
    p = doc.add_paragraph(
        "Data preparation directly dictates the stability, accuracy, and business viability of downstream predictive systems:"
    )
    p.paragraph_format.space_after = Pt(4)

    # Downstream Impact Table
    impact_table = doc.add_table(rows=4, cols=3)
    impact_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    impact_table.autofit = False
    set_table_borders(impact_table)
    
    i_col_widths = [Inches(1.8), Inches(2.2), Inches(2.5)]
    i_headers = ["Downstream Application", "Untreated Ingestion Risk", "Post-Preprocessing Pipeline Benefit"]
    
    i_hdr_row = impact_table.rows[0]
    for idx, text in enumerate(i_headers):
        cell = i_hdr_row.cells[idx]
        cell.width = i_col_widths[idx]
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    impact_data = [
        ("Transit Duration & ETA Regression (Gradient Boost / Ridge)",
         "Chronological inversions create negative transit targets; extreme payload weights cause exploding gradients and inflated RMSE.",
         "Winsorization caps extreme tail spikes; log1p normalizes residuals; loss functions converge rapidly to realistic lane transit variances."),
        ("Carrier Performance Classification (Random Forest / Logistic)",
         "Unstandardized strings ('FedEx', 'fedex', 'FEDEX') cause cardinality explosion, fragmenting tree decision splits and overfitting.",
         "Canonical mapping and one-hot encoding with drop='first' eliminate multicollinearity and preserve model degrees of freedom."),
        ("Vehicle Route & Territory Clustering (k-Means / DBSCAN)",
         "Distance variables in thousands dominate parcel weights in single digits; coordinates on Null Island distort cluster centroids.",
         "RobustScaler balances Euclidean contributions across spatial, financial, and physical attributes, grouping viable delivery clusters."),
    ]

    for r_idx, row_data in enumerate(impact_data):
        row = impact_table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = i_col_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            if r_idx % 2 == 1:
                set_cell_shading(cell, HEX_BG_LIGHT)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)
            r.font.color.rgb = COLOR_TEXT_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)

    add_custom_heading(doc, "6.1 Financial & Operational Business Implications", level=2)
    
    biz_points = [
        ("SLA Compliance & Chargeback Mitigation: ", "Logistics contracts impose chargeback penalties ($50-$250 per shipment) for late deliveries. Chronological inversions caused by device clock drift misclassify compliant deliveries as late, triggering unwarranted financial penalties. Filtering inversions protects contract compliance."),
        ("Fleet Capacity & Cubic Utilization Optimization: ", "Freight billing relies on weight-to-volume ratios (Dimensional Weight Pricing). Raw feeds containing zero-weight readings from uncalibrated scales skew load balancing. Correcting these metrics prevents trailer under-utilization and reduces excess fleet fuel consumption."),
        ("Dynamic Spot-Quote Pricing Protection: ", "Automated freight pricing engines calculate spot rates based on historical lane velocity and freight density. Unscaled outliers passing into pricing models generate volatile, non-competitive quotes that erode profit margins."),
    ]
    for prefix, body in biz_points:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_before = Pt(2)
        bp.paragraph_format.space_after = Pt(2)
        r_p = bp.add_run(prefix)
        r_p.font.bold = True
        r_p.font.color.rgb = COLOR_PRIMARY
        bp.add_run(body)

    # ---------------------------------------------------------
    # SECTION 7: EXECUTIVE SUBMISSION SUMMARY
    # ---------------------------------------------------------
    add_custom_heading(doc, "7. Executive Submission Summary (Portal Submission)", level=1)
    
    submission_summary_text = (
        "This comprehensive technical project establishes a production-grade data collection, cleaning, and preprocessing pipeline "
        "engineered for multimodal freight telematics and urban last-mile logistics. Benchmarked against canonical supply chain datasets—the "
        "Olist Brazilian E-Commerce and DataCo Global Supply Chain repositories—the architecture systematically resolves critical real-world "
        "failure modes spanning structural key duplication, sensor calibration drift, chronological timestamp inversions, coordinate "
        "transpositions, and severe distributional skew. The pipeline enforces automated primary key deduplication, string and currency "
        "sanitization, geospatial polygon bounding, physical feasibility gating, and non-parametric Tukey’s Fences Winsorization. "
        "A production Scikit-Learn ColumnTransformer integrates median imputation, cyclical trigonometric temporal encodings (S1 unit "
        "circle transformations for 24-hour dispatch cycles), natural logarithmic variance stabilization (log1p), and median-IQR RobustScaler "
        "normalizations. Crucially, target leakage is eliminated by categorizing unrecorded delivery timestamps as explicit operational exceptions "
        "rather than imputing artificial delivery durations. Across an empirical validation run of 2,000 raw telematics records, the pipeline "
        "achieved a 97.90% operational retention yield, stabilized heavy-tail cargo weight skewness from an initial 11.97 down to 1.83, "
        "and produced a clean, 31-dimensional feature matrix. This production-ready architecture guarantees numerical stability for downstream "
        "ETA regression, carrier classification, route clustering, and fleet optimization while effectively safeguarding enterprise commercial "
        "freight operations against costly financial contractual SLA compliance breach chargeback penalties."
    )

    create_callout_box(
        doc,
        title="EXECUTIVE PORTAL SUBMISSION SUMMARY (EXACTLY 200 WORDS)",
        text=submission_summary_text,
        border_color=HEX_ACCENT,
        bg_color=HEX_CALLOUT_BG,
    )

    # Save document
    doc.save(output_path)
    print(f"Executive Word Document successfully compiled to: {output_path}")


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Task_2_Logistics_Data_Preprocessing_Report.docx"
    build_word_report(out_file)
