import yaml
from io import BytesIO
from date_helper import DateHelper
from pypdf import PdfWriter
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import LETTER, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

### GLOBAL VALUES, LOAD DATA AND PARSE ###

SAVE_NAME = 'out.pdf'
DATA_FILE_NAME = "data.yml"

with open(DATA_FILE_NAME, 'r') as file:
    data_raw = yaml.safe_load(file)

#print(data_raw) # uncomment for debug print

date_obj = DateHelper()

# Generates one page and returns a byte stream representation of it
def gen_document() -> BytesIO:

    ### VARIABLES AND INITIAL INSTANTIATION ###

    buffer = BytesIO()

    weekday = date_obj.get_offset_as_weekday()
    date_text_raw = date_obj.get_date()

    doc = SimpleDocTemplate(buffer)
    doc.pagesize = portrait(LETTER)

    elements = []

    ### HEADER ###

    header_style = ParagraphStyle('HeaderStyle', fontSize = 16, alignment = TA_CENTER)
    header_text = Paragraph('<b><u>Cleaning Tasks (Daypart Assignments)</u></b>', header_style)

    date_style = ParagraphStyle('DateStyle', fontSize = 14, alignment = TA_CENTER)
    date_text = Paragraph(date_text_raw, date_style)

    header = Table([[header_text], [date_text]], colWidths=None)
    header.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.125 * inch)]))

    ##################
    ### DATA TABLE ###
    ##################

    style = TableStyle([
        ('ALIGN',(0, 0),(-1,-1),'CENTER'),
        ('VALIGN',(0, 0),(-1,-1),'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, black),
        ('BOX', (0,0), (-1,-1), 0.25, black),
        ('LEFTPADDING', (0, 0), (-1, -1), inch),
        ('RIGHTPADDING', (0, 0), (-1, -1), inch)])

    # Generate the daily tasks from the parsed data
    # Start with daily tasks
    am_tasks = list(data_raw['daily']['AM'])
    mid_tasks = list(data_raw['daily']['MID'])
    pm_tasks = list(data_raw['daily']['PM'])

    # Check for weekday specific tasks
    if weekday in data_raw:
        if 'AM' in data_raw[weekday]:
            for am in data_raw[weekday]['AM']:
                am_tasks.append(am)
        if 'MID' in data_raw[weekday]:
            for mid in data_raw[weekday]['MID']:
                mid_tasks.append()
        if 'PM' in data_raw[weekday]:
            for pm in data_raw[weekday]['PM']:
                pm_tasks.append(pm)
     
    mid_index = 1
    pm_index = 2

    data = [['AM (open-11)', 'Initials',]]

    for a in am_tasks:
        data.append([str(a), ''])
        mid_index += 1
        pm_index += 1

    data.append(['MID (11-2)', ''])

    for b in mid_tasks:
        data.append([str(b), ''])
        pm_index += 1

    data.append(['PM (2-close)', ''])

    for c in pm_tasks:
        data.append([str(c), ''])

    # The first style set will always be the same
    # The next two have to be determined programatically
    style.add('FONT', (0, 0), (1, 0), 'Helvetica-Bold')
    style.add('FONT', (0, mid_index), (0, mid_index), 'Helvetica-Bold')
    style.add('FONT', (0, pm_index), (0, pm_index), 'Helvetica-Bold')

    t = Table(data)
    t.setStyle(style)

    ### INVENTORY TRACKING ###

    inventory_style = ParagraphStyle('InvStyle', fontSize = 11, alignment = TA_CENTER)
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

# Run the function 7 times; updates for days of week and conditionals are all taken care of

merger = PdfWriter()
for _ in range(7):
    page = gen_document()
    merger.append(page)

merger.write(SAVE_NAME)
merger.close()
