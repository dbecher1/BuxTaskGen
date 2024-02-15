import yaml
from io import BytesIO
from simple_date_helper import SimpleDate
from pypdf import PdfWriter
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import LETTER, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

### GLOBAL VALUES, LOAD DATA AND PARSE ###

SAVE_NAME_FINAL = 'out.pdf'
DATA_FILE_NAME = "data.yml"

with open(DATA_FILE_NAME, 'r') as file:
    data_raw = yaml.safe_load(file)

print(data_raw) # uncomment for debug print

m = data_raw['month']
d = data_raw['date']
y = data_raw['year']
date_obj = SimpleDate(m, d, y)

# TODO: remove dummy data once yaml parsing is implemented

def gen_document():

    ### VARIABLES AND INITIAL INSTANTIATION ###

    buffer = BytesIO()

    weekday = date_obj.get_offset_as_weekday()
    date_text_raw = date_obj.get_date()

    doc = SimpleDocTemplate(buffer,
                            pagesize=LETTER,
                            rightMargin=30,
                            leftMargin=30,
                            topMargin=30,
                            bottomMargin=18)
    doc.pagesize = portrait(LETTER)

    elements = []

    ### HEADER ###

    header_style = ParagraphStyle('HeaderStyle',
                        fontSize = 16,
                        alignment = TA_CENTER,
                        )
    header_text = Paragraph('<b><u>Cleaning Tasks (Daypart Assignments)</u></b>', header_style)

    date_style = ParagraphStyle('DateStyle',
                        fontSize = 14,
                        alignment = TA_CENTER,
                        )
    date_text = Paragraph(date_text_raw, date_style)

    header = Table([[header_text], [date_text]], colWidths=None)
    header.setStyle(
        TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.125 * inch)
        ])
    )

    ### DATA TABLE ###

    style = TableStyle([
        ('ALIGN',(0, 0),(-1,-1),'CENTER'),
        ('VALIGN',(0, 0),(-1,-1),'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, black),
        ('BOX', (0,0), (-1,-1), 0.25, black),
        ('LEFTPADDING', (0, 0), (-1, -1), inch),
        ('RIGHTPADDING', (0, 0), (-1, -1), inch),
        #('FONT', (0, 0), (-1, -1), 'Times-Bold'),
        ])

    # The first style set will always be the same
    style.add('FONT', (0, 0), (1, 0), 'Helvetica-Bold')

    # Generate the daily tasks from the parsed data
    # Start with daily tasks
    am_tasks = data_raw['daily']['AM']
    mid_tasks = data_raw['daily']['MID']
    pm_tasks = data_raw['daily']['PM']

    # Check for weekday specific tasks
    if weekday in data_raw:
        weekday_specific_tasks = data_raw[weekday]
        if 'AM' in weekday_specific_tasks:
            am_tasks.append(weekday_specific_tasks['AM'])
        if 'MID' in weekday_specific_tasks:
            mid_tasks.append(weekday_specific_tasks['MID'])
        if 'PM' in weekday_specific_tasks:
            pm_tasks.append(weekday_specific_tasks['PM'])

    # The next two have to be determined programatically
    style.add('FONT', (0, 3), (0, 3), 'Helvetica-Bold')

    data = [
    ["AM (open-11)", "Initials",],
    ["Front of House Drains", "",],
    ["Front of House Drains", "",],
    ["Mid (11-2)", "",],
    ["Front of House Drains", "",],
    ]

    t = Table(data)
    t.setStyle(style)

    ### INVENTORY TRACKING ###

    inventory_style = ParagraphStyle('InvStyle',
                        fontSize = 12,
                        alignment = TA_CENTER,
                        )
    inventory_text = Paragraph("<b>Inventory Tracking: Low Stock and Outages (write below)</b>", inventory_style)

    ### CREATE FORMAT TABLE ###

    format_table = Table([[header], [t], [inventory_text]], colWidths=None)
    format_table.setStyle(
        TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.25 * inch)
        ])
    )
    elements.append(format_table)

    ### SAVE FILE ###

    doc.build(elements)
    return buffer

merger = PdfWriter()
for _ in range(7):
    page = gen_document()
    merger.append(page)

merger.write(SAVE_NAME_FINAL)
merger.close()
