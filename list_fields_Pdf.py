import fitz  # PyMuPDF
import pprint

form_template = 'Formulaire_EC_template.pdf'

doc = fitz.open(form_template)
for page in doc:
    for field in page.widgets():
        print(field.field_name)
        pprint.pprint(field)
doc.close()
