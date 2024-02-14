from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import LETTER, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

SAVE_NAME = 'test.pdf'

doc = SimpleDocTemplate(SAVE_NAME,
                        pagesize=LETTER,
                        rightMargin=30,
                        leftMargin=30,
                        topMargin=30,
                        bottomMargin=18)
doc.pagesize = portrait(LETTER)
elements = []

data = [
["AM (open-11)", "Initials",],
["Front of House Drains", "",],
["Front of House Drains", "",],
["Mid (11-2)", "",],
["Front of House Drains", "",],
]

test = ParagraphStyle('Style',
                      fontSize = 16,
                      alignment = TA_CENTER,
                      )
p = Paragraph('Lolololol', test)
elements.append(p)

style = TableStyle([
    ('ALIGN',(0, 0),(-1,-1),'CENTER'),
    ('VALIGN',(0, 0),(-1,-1),'MIDDLE'),
    ('INNERGRID', (0,0), (-1,-1), 0.25, black),
    ('BOX', (0,0), (-1,-1), 0.25, black),
    ('LEFTPADDING', (0, 0), (-1, -1), 50),
    ('RIGHTPADDING', (0, 0), (-1, -1), 50),
    #('FONT', (0, 0), (-1, -1), 'Times-Bold'),
    ])

style.add('FONT', (0, 0), (0, 0), 'Helvetica-Bold')
style.add('FONT', (0, 3), (0, 3), 'Helvetica-Bold')

t=Table(data)
t.setStyle(style)

#Send the data and build the file
elements.append(t)
doc.build(elements)