import json
import fitz  # PyMuPDF
from pathlib import Path

TEMPLATE = 'Formulaire_EC_template.pdf'  # votre modèle
INPUT_JSON = 'ec_data.json'              # données collaborateurs
OUTPUT_DIR = Path('ec_outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fill_pdf(template_path: str, output_path: str, data: dict):
    doc = fitz.open(template_path)
    for page in doc:
        widgets = page.widgets() or []
        for w in widgets:
            fname = w.field_name
            if not fname:
                continue
            if fname in data and data[fname] is not None:
                val = str(data[fname])
                try:
                    w.field_value = val
                    w.update()
                except Exception as e:
                    print(f"Warn: could not set {fname}: {e}")
    doc.save(output_path)
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
    'PERNR': 'pernr',
    'DATE_PERIODE_DU_af_date': 'periode_du',
    'DATE_PERIODE_AU_af_date': 'periode_au',
    'DATE_ENTRETIEN_af_date': 'date_entretien',
    'Motif/période de référence': 'motif',

    # Points clés (zone commentaires)
    'COM_BILAN': 'point3_buts_responsabilites',

    # Compétences (10 lignes commentées; étendre si vous voulez couvrir plus)
    'COM_COMP_01': 'point4_comp_01',
    'COM_COMP_02': 'point4_comp_02',
    'COM_COMP_03': 'point4_comp_03',
    'COM_COMP_04': 'point4_comp_04',
    'COM_COMP_05': 'point4_comp_05',
    'COM_COMP_06': 'point4_comp_06',
    'COM_COMP_07': 'point4_comp_07',
    'COM_COMP_08': 'point4_comp_08',
    'COM_COMP_09': 'point4_comp_09',
    'COM_COMP_10': 'point4_comp_10',
}

DEFAULTS = {
    'CC_STATUT': 'Collaborateur',
    'CC_TAD': 'Non',
    'Motif/période de référence': 'Période de référence',
}

def build_pdf_payload(collab: dict) -> dict:
    mapping = {}
    for pdf_field, json_key in FIELD_MAP.items():
        val = collab.get(json_key)
        if (val is None or val == '') and pdf_field in DEFAULTS:
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
