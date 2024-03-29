import yaml
import datetime
from io import BytesIO
from pypdf import PdfWriter
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import LETTER, portrait, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

### GLOBAL VALUES, LOAD DATA AND PARSE ###

WEEKDAY_ENUM = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday']

# Date object: set to monday if today is not monday
today = datetime.date.today()
if today.weekday() != 0:
    today = today - datetime.timedelta(days=today.weekday())

DATA_FILE_NAME = "input.yml"

with open(DATA_FILE_NAME, 'r') as file:
    data_raw = yaml.safe_load(file)

use_date = data_raw['use_date']

if use_date:
    # If using date go to nearest monday
    if today.weekday() != 0:
        today = today - datetime.timedelta(days=today.weekday())
    SAVE_NAME = 'out/' + str(today) + '.pdf'
else:
    # If not just use today's date in the filename
    SAVE_NAME = 'out/' + 'nodate_' + str(today) + '.pdf'

# Generates one page and returns a byte stream representation of it
def gen_document() -> BytesIO:

    ### VARIABLES AND INITIAL INSTANTIATION ###
    global today
    buffer = BytesIO()

    # weekdays are stored in lower case in the YAML file
    weekday = WEEKDAY_ENUM[today.weekday()].lower()
    date_text_raw = '{}, {}/{}'.format(
            WEEKDAY_ENUM[today.weekday()],
            today.month % 10 if today.month < 10
            else today.month,
            today.day)
    
    # increment the day for the next loop iteration
    today = today + datetime.timedelta(days=1)

    # PDF variables
    doc = SimpleDocTemplate(buffer)
    doc.pagesize = landscape(LETTER)
    elements = []

    #######################
    ### DOCUMENT HEADER ###
    #######################

    header_style = ParagraphStyle('HeaderStyle', fontSize = 16, alignment = TA_CENTER)
    header_text = Paragraph('<b><u>Cleaning Tasks (Daypart Assignments)</u></b>', header_style)

    date_style = ParagraphStyle('DateStyle', fontSize = 14, alignment = TA_CENTER)
    date_text = Paragraph(date_text_raw, date_style)

    if use_date:
        header = Table([[header_text], [date_text]], colWidths=None)
    else:
        header = Table([[header_text]], colWidths=None)
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

    # Check for weekday specific tasks if using date
    if use_date and weekday in data_raw:
        if 'AM' in data_raw[weekday]:
            for am in data_raw[weekday]['AM']:
                am_tasks.append(am)
        if 'MID' in data_raw[weekday]:
            for mid in data_raw[weekday]['MID']:
                mid_tasks.append(mid)
        if 'PM' in data_raw[weekday]:
            for pm in data_raw[weekday]['PM']:
                pm_tasks.append(pm)
    elif not use_date:
        # Manually enumerate through the weekdays and add tasks if they exist in the YAML
        for wd in [str.lower(w) for w in WEEKDAY_ENUM if w.lower() in data_raw]:

            # quick and dirty implementation, could be done with less code reuse so maybe TODO eventually

            if 'AM' in data_raw[wd]:
                for am in [a for a in data_raw[wd]['AM'] if a not in am_tasks]:
                    # Make sure no dup
                    am_tasks.append(am)
            if 'MID' in data_raw[wd]:
                for mid in [m for m in data_raw[wd]['MID'] if m not in mid_tasks]:
                    mid_tasks.append(mid)
            if 'PM' in data_raw[wd]:
                for pm in [p for p in data_raw[wd]['PM'] if p not in pm_tasks]:
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

# Run the function 7 times to populate the week or once if no date

if use_date:
    page_ct = 7
else:
    page_ct = 1

merger = PdfWriter()

for _ in range(page_ct):
    page = gen_document()
    merger.append(page)

merger.write(SAVE_NAME)
merger.close()
