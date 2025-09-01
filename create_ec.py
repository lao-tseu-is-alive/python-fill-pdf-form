import json
import fitz  # PyMuPDF
from pathlib import Path

TEMPLATE = 'Formulaire_EC_template.pdf'
INPUT_JSON = 'ec_data.json'
OUTPUT_DIR = Path('ec_outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fill_pdf(template_path: str, output_path: str, data: dict):
    doc = fitz.open(template_path)
    processed_fields = set()  # Keep track of fields that have been processed

    for page in doc:
        widgets = page.widgets() or []
        for w in widgets:
            fname = w.field_name
            if not fname or fname in processed_fields:
                continue

            if fname in data and data[fname] is not None:
                val = str(data[fname])
                try:
                    # This single line handles all field types, including radio groups
                    w.field_value = val
                    w.update()
                    # Once a field (like a radio group) is set, add it to the processed set
                    processed_fields.add(fname)
                except Exception as e:
                    print(f"Warn: could not set {fname}: {e}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

def load_json(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Association champs PDF -> clés JSON
FIELD_MAP = {
    # Partie administrative
    'Nom_Prénom': 'nom_prenom',
    'CC_STATUT': 'statut',
    'CC_TAD': 'travail_distance',            # ex: Oui/Non
    'SI_TAD_O': 'travail_distance_option',   # si pertinent
    'Poste': 'poste',
    'Service': 'service',
    'Taux': 'taux',
    'PERNR': 'salarie_num',
    'DATE_PERIODE_DU_af_date': 'periode_du',
    'DATE_PERIODE_AU_af_date': 'periode_au',
    'DATE_ENTRETIEN_af_date': 'date_entretien',
    'Motif/période de référence': 'motif',

    # Buts et responsabilites (dans les commentaires)
    'COM_03_A01': 'point3_buts_01',
    'COM_03_A02': 'point3_buts_02',
    'COM_03_A03': 'point3_buts_03',
    'COM_03_A04': 'point3_buts_04',
    'COM_03_A05': 'point3_buts_05',
    'COM_03_A06': 'point3_buts_06',

    # Compétences
    'COMP_FAM_01': 'point4_comp_01_cat',
    'COMP_LNG_01': 'point4_comp_01_comp',
    'COMP_FAM_02': 'point4_comp_02_cat',
    'COMP_LNG_02': 'point4_comp_02_comp',
    'COMP_FAM_03': 'point4_comp_03_cat',
    'COMP_LNG_03': 'point4_comp_03_comp',
    'COMP_FAM_04': 'point4_comp_04_cat',
    'COMP_LNG_04': 'point4_comp_04_comp',
    'COMP_FAM_05': 'point4_comp_05_cat',
    'COMP_LNG_05': 'point4_comp_05_comp',
    'COMP_FAM_06': 'point4_comp_06_cat',
    'COMP_LNG_06': 'point4_comp_06_comp',
    'COMP_FAM_07': 'point4_comp_07_cat',
    'COMP_LNG_07': 'point4_comp_07_comp',
    'COMP_FAM_08': 'point4_comp_08_cat',
    'COMP_LNG_08': 'point4_comp_08_comp',
    'COMP_FAM_09': 'point4_comp_09_cat',
    'COMP_LNG_09': 'point4_comp_09_comp',
    'COMP_FAM_10': 'point4_comp_10_cat',
    'COMP_LNG_10': 'point4_comp_10_comp',
}

DEFAULTS = {
    'CC_STATUT': 'Collaborateur#B7trice', # Valeur corrigée
    'CC_TAD': 'Non',
    'Motif/période de référence': 'Période de référence',
}

def build_pdf_payload(collab: dict) -> dict:
    mapping = {}
    for pdf_field, json_key in FIELD_MAP.items():
        val = collab.get(json_key)
        if (val is None or str(val).strip() == '') and pdf_field in DEFAULTS:
            val = DEFAULTS[pdf_field]
        mapping[pdf_field] = val
    return mapping

def main():
    payload = load_json(INPUT_JSON)
    for collab in payload:
        stub = collab.get('filename_stub') or collab.get('nom_prenom', 'collaborateur').replace(' ', '_')
        out_path = OUTPUT_DIR / f"2025_Formulaire_EC_{stub}.pdf"
        pdf_data = build_pdf_payload(collab)
        fill_pdf(TEMPLATE, str(out_path), pdf_data)
        print(f"Generated: {out_path}")

if __name__ == '__main__':
    main()