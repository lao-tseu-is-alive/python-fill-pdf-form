import json
import re
import pymupdf
from pathlib import Path

TEMPLATE = 'Formulaire_EC_template.pdf'
INPUT_JSON = 'ec_data.json'
OUTPUT_DIR = Path('ec_outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TAD_ANNEX_FIELD = 'P1.ANNEXE1.COM_POSITIF'  # only on the "ANNEXE 1 – Travail à distance" page (Nom_2/Poste_2 are also on page 8)
TAD_ANNEX_LINK_FIELD = 'SI_TAD_O'     # "Voir ANNEXE 1" button, shown by Acrobat JS only when CC_TAD == Oui

def normalize_state(s: str) -> str:
    # 'Collaborateur#B7trice', 'collaborateur-trice' -> 'collaborateurtrice' ; 'Cadre' -> 'cadre'
    return re.sub(r'[^a-z]', '', s.lower().replace('#b7', ''))

def set_radio(doc, fname: str, kids: list, value: str):
    # PyMuPDF turns ON any radio widget given a non-empty value, and cannot write
    # names such as 'Collaborateur#B7trice': set /AS of each kid and /V of the group directly.
    target = normalize_state(value)
    on_states = {on for _, on in kids}
    chosen = next((s for s in on_states if normalize_state(s) == target), None)
    if chosen is None:
        print(f"Warn: no option matching '{value}' for {fname} (options: {sorted(on_states)})")
        return
    for xref, on in kids:
        doc.xref_set_key(xref, 'AS', f'/{chosen}' if on == chosen else '/Off')
        doc.xref_set_key(parent_xref(doc, xref) or xref, 'V', f'/{chosen}')

def parent_xref(doc, xref: int) -> int | None:
    parent = doc.xref_get_key(xref, 'Parent')
    return int(parent[1].split()[0]) if parent[0] == 'xref' else None

def pdf_refs(array: str) -> list[int]:
    # '[12 0 R 34 0 R]' -> [12, 34]
    return [int(x) for x in re.findall(r'(\d+) 0 R', array)]

def detach_field(doc, xref: int):
    # Remove a field from its parent's /Kids (or from /AcroForm /Fields), pruning parents left empty,
    # so that deleting a page does not leave orphan fields pointing to it.
    parent = parent_xref(doc, xref)
    # xref_set_key() cannot write through a path such as 'AcroForm/Fields': resolve the AcroForm object
    holder, key = (parent, 'Kids') if parent else (pdf_refs(doc.xref_get_key(doc.pdf_catalog(), 'AcroForm')[1])[0], 'Fields')
    kids = [k for k in pdf_refs(doc.xref_get_key(holder, key)[1]) if k != xref]
    if parent and not kids:
        detach_field(doc, parent)
    else:
        doc.xref_set_key(holder, key, '[' + ' '.join(f'{k} 0 R' for k in kids) + ']')

def adjust_tad_annex(doc, teletravail: bool):
    annex = next(p.number for p in doc for w in p.widgets() if w.field_name == TAD_ANNEX_FIELD)
    links = [w.xref for p in doc for w in p.widgets() if w.field_name == TAD_ANNEX_LINK_FIELD]
    if teletravail:
        for xref in links:
            doc.xref_set_key(xref, 'F', '4')  # print, no longer hidden
        return
    for xref in links:
        doc.xref_set_key(xref, 'AA', 'null')  # drop the GoTo towards the removed page
    for xref in [w.xref for w in doc[annex].widgets()]:
        detach_field(doc, xref)
    doc.delete_page(annex)

def fill_pdf(template_path: str, output_path: str, data: dict):
    doc = pymupdf.open(template_path)
    radio_groups = {}  # field name -> [(xref, on_state)] of every kid of the group (across pages)

    for page in doc:
        widgets = page.widgets() or []
        for w in widgets:
            fname = w.field_name
            if not fname or data.get(fname) in (None, ''):  # empty: keep the template's value
                continue

            if w.field_type == pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON:
                radio_groups.setdefault(fname, []).append((w.xref, w.on_state()))
                continue

            try:
                w.field_value = str(data[fname])
                w.update()
            except Exception as e:
                print(f"Warn: could not set {fname}: {e}")

    for fname, kids in radio_groups.items():
        set_radio(doc, fname, kids, str(data[fname]))
    adjust_tad_annex(doc, normalize_state(str(data.get('CC_TAD', ''))) == 'oui')
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

    # Annexe 1 (travail à distance) : en-tête recopié par JavaScript Acrobat, que PyMuPDF n'exécute pas
    'P1.ANNEXE1.Nom_2': 'nom_prenom',
    'P1.ANNEXE1.Poste_2': 'poste',
    'P1.ANNEXE1.Service_2': 'service',
    'P1.ANNEXE1.Taux_2': 'taux',
    'P1.ANNEXE1.PERNR_2': 'salarie_num',
    'P1.ANNEXE1.DATE_PERIODE_DU_2_af_date': 'periode_du',
    'P1.ANNEXE1.DATE_PERIODE_AU_2_af_date': 'periode_au',
    'P1.ANNEXE1.DATE_ENTRETIEN_2_af_date': 'date_entretien',
    'P1.ANNEXE1.PERIODE_REF': 'motif',

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
DEFAULTS['P1.ANNEXE1.PERIODE_REF'] = DEFAULTS['Motif/période de référence']

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
        year = str(collab.get('periode_au', '')).strip()[-4:]
        if not year.isdigit():
            raise ValueError(f"{stub}: 'periode_au' must be a date dd.mm.yyyy, got {collab.get('periode_au')!r}")
        out_path = OUTPUT_DIR / f"{year}_Formulaire_EC_{stub}.pdf"
        pdf_data = build_pdf_payload(collab)
        fill_pdf(TEMPLATE, str(out_path), pdf_data)
        print(f"Generated: {out_path}")

if __name__ == '__main__':
    main()