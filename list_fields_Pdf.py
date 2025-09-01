import fitz  # PyMuPDF

form_template = 'Formulaire_EC_template.pdf'

doc = fitz.open(form_template)
print("page, field_label, field_name, field_type, field_type_string, field_value, choice_values, button_states")
for page in doc:

    for w in page.widgets():
        print(f"'{page}', '{w.field_label}','{w.field_name}', {w.field_type}, '{w.field_type_string}', '{w.field_value}', {w.choice_values}, {w.button_states()}")
doc.close()
