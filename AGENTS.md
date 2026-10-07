# AGENTS.md

Notes pour les agents de code travaillant sur ce dépôt. Pour l'usage général, voir `README.md`.

## Projet

`create_ec.py` remplit le formulaire PDF « Entretien de collaboration » de la Ville de Lausanne (`Formulaire_EC_template.pdf`, 12 pages, AcroForm conçu pour Acrobat) à partir de `ec_data.json` : un PDF par personne dans `ec_outputs/`.

- Environnement : uv, Python 3.13, `pymupdf` (importé sous le nom `pymupdf`, pas `fitz` qui est déprécié).
- Lancer : `uv run create_ec.py`. Lister les champs du modèle : `uv run list_fields_Pdf.py`.
- Le mapping champ PDF → clé JSON est dans `FIELD_MAP`, les valeurs par défaut dans `DEFAULTS`.

## Confidentialité (impératif)

- `ec_data.json`, `ec_data_<année>.json`, `data/` et `ec_outputs*/` contiennent des données personnelles (évaluations RH) : ils sont dans `.gitignore` et ne doivent **jamais** être commités, copiés dans un fichier suivi ni cités dans un message de commit.
- Seul `ec_data_anonymised.json` est un exemple versionné ; il doit rester anonymisé.
- Pour tester, générer dans un dossier temporaire (en surchargeant `create_ec.OUTPUT_DIR`) plutôt que d'écraser `ec_outputs/`.

## Pièges connus de PyMuPDF et du modèle

1. **Boutons radio (`CC_STATUT`, `CC_TAD`)** : `widget.field_value = <n'importe quelle chaîne non vide>` coche *ce* widget, quelle que soit la valeur. Ne jamais remplir un radio par `field_value` : `set_radio()` écrit directement `/AS` sur chaque widget et `/V` sur le parent.
2. **`Collaborateur#B7trice`** : l'état « on » du statut contient l'octet `0xB7` (`·`). PyMuPDF ne peut pas le passer à `pdf_set_field_value` (`TypeError ... char const *`), et `xref_get_key` le renvoie avec un caractère de substitution (`\udcb7`) : utiliser `ascii()` ou `PYTHONIOENCODING=utf-8:backslashreplace` pour l'afficher. `normalize_state()` compare les valeurs sans casse ni ponctuation.
3. **Les widgets ne survivent pas à leur page** : un `Widget` gardé après être passé à la page suivante lève `ReferenceError: weakly-referenced object no longer exists`. Conserver des `xref` (et `on_state()` calculé tout de suite), pas des objets `Widget`.
4. **`xref_set_key()` avec un chemin** (`'AcroForm/Fields'`) corrompt la valeur (`fitz: replace me!`) : résoudre d'abord l'objet (`AcroForm` → xref) puis écrire la clé `Fields`.
5. **JavaScript non exécuté** : le modèle utilise des scripts Acrobat (champs calculés de l'Annexe 1, visibilité du bouton `SI_TAD_O` « Voir ANNEXE 1 »). PyMuPDF ne les exécute pas : tout ce qui doit apparaître doit être rempli ou rendu visible explicitement par le script.
6. **Champs partagés entre pages** : un même nom de champ peut avoir plusieurs widgets. `P1.ANNEXE1.Nom_2` et `P1.ANNEXE1.Poste_2` sont aussi sur la page 8 (bloc signatures) ; `CC_TAD` est sur les pages 1, 8 et 10 ; `CC_STATUT` sur les pages 1 et 10.
7. **Listes déroulantes `COMP_FAM_XX`** : les options sont des paires (export, libellé), p. ex. `('METHO', 'Méthodologiques')`. Le JSON fournit le libellé, qui doit correspondre exactement (au pluriel).

## Annexe 1 – Travail à distance

`adjust_tad_annex()` (appelée en fin de `fill_pdf()`) :

- télétravail `Oui` : rend visibles les boutons `SI_TAD_O` (`/F 4`) ;
- sinon : neutralise leur action GoTo, détache les champs de la page de l'annexe (`detach_field()`, qui élague les parents vides) puis supprime la page.

La page est repérée par `TAD_ANNEX_FIELD = 'P1.ANNEXE1.COM_POSITIF'`, champ présent uniquement sur l'annexe. Ne pas utiliser `Nom_2` ou `Poste_2` : ils sont aussi sur la page 8, qui serait supprimée à tort.

Le modèle contient déjà 26 widgets orphelins (référencés par l'AcroForm mais sur aucune page) et des références (balisage d'accessibilité, destination nommée `ANNEXE1`) qui gardent l'objet de page supprimé dans le fichier : c'est attendu et sans effet visible.

## Vérification après modification

Toujours vérifier le résultat réel, pas seulement l'absence d'erreur :

- lire `/AS` des widgets `CC_STATUT` / `CC_TAD` (`doc.xref_get_key(w.xref, 'AS')`) et le comparer aux données ;
- nombre de pages : 12 avec télétravail, 11 sans ; le titre « ANNEXE 1 » ne doit plus apparaître dans les PDF sans télétravail, et la page 8 (« Page 8 sur 8 », signatures) doit toujours être présente ;
- compter les widgets orphelins : il ne doit pas y en avoir plus que les 26 du modèle ;
- comparer les champs remplis avec les PDF de l'année précédente (`ec_outputs_<année>/`) pour détecter une perte de données ;
- en cas de doute, faire un rendu de page (`page.get_pixmap(...)`) et le regarder.

## Pistes d'amélioration (prochaine itération)

- **Script de vérification `check_ec.py`** : automatiser les contrôles ci-dessus (états `/AS` des radios comparés au JSON, nombre de pages selon le télétravail, présence de la page 8, nombre de widgets orphelins, comparaison champ par champ avec `ec_outputs_<année précédente>/`), lançable par `uv run check_ec.py` après chaque génération. Ces contrôles, faits à la main en 2026, ont révélé que tous les PDF 2025 avaient un statut et un télétravail erronés.
- Régénérer `field_list.txt` avec la version actuelle de PyMuPDF (seul le format d'affichage des pages a changé).
- Supprimer ou utiliser la clé JSON `pernr`, actuellement ignorée (le champ `PERNR` est rempli par `salarie_num`).
