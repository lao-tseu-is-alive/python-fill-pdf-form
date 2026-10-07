# python-fill-pdf-form

### Remplissage Automatisé de formulaire PDF avec Python

Ce projet est un exemple de script Python qui permet de remplir automatiquement des formulaires PDF en utilisant des données structurées au format JSON. C'est une solution idéale pour automatiser la génération de documents répétitifs tels que des formulaires administratifs, des factures, ou des certificats.

## Fonctionnalités

-   **Remplissage de champs de formulaire** : Supporte les champs de texte, les menus déroulants, les cases à cocher et les boutons radio.
-   **Gestion de données externes** : Utilise un fichier JSON pour fournir les données, ce qui facilite la gestion et la mise à jour des informations.
-   **Génération de multiples PDF** : Capable de générer plusieurs documents PDF remplis en une seule exécution, chacun avec ses propres données.
-   **Personnalisable** : Facilement adaptable pour fonctionner avec n'importe quel formulaire PDF.

## Prérequis

Le projet est géré avec [uv](https://docs.astral.sh/uv/) (Python 3.13, dépendance `PyMuPDF`). Pour installer l'environnement :

```bash
uv sync
```

## Utilisation

1.  **Préparez votre modèle PDF** : Placez votre formulaire PDF vierge à la racine du projet et nommez-le `Formulaire_EC_template.pdf`.

2.  **Préparez vos données** : Créez un fichier `ec_data.json` contenant les données à insérer dans le PDF. Vous pouvez vous inspirer du fichier `ec_data_anonymised.json` pour la structure.

3.  **Lancez le script** : Exécutez le script `create_ec.py` depuis votre terminal.

    ```bash
    uv run create_ec.py
    ```

4.  **Récupérez les PDF générés** : Les nouveaux fichiers PDF remplis seront créés dans le dossier `ec_outputs`, sous le nom `<année>_Formulaire_EC_<filename_stub>.pdf`. L'année est celle de `periode_au` : les PDF d'une autre année ne sont donc pas écrasés.

## Valeurs attendues dans le JSON

| Clé | Valeurs | Remarque |
|---|---|---|
| `statut` | `cadre` ou `collaborateur-trice` | Casse et ponctuation ignorées (`Cadre`, `Collaborateur#B7trice` sont aussi acceptés). Par défaut : collaborateur·trice. |
| `travail_distance` | `Oui` ou `Non` | Par défaut : `Non`. Détermine la présence de l'Annexe 1 (voir ci-dessous). |
| `periode_du`, `periode_au`, `date_entretien` | `jj.mm.aaaa` | `periode_au` est obligatoire : il donne l'année du nom de fichier. |
| `point4_comp_XX_cat` | `Personnelles`, `Méthodologiques`, `Relationnelles`, `Managériales` | Libellés exacts de la liste déroulante du formulaire (au pluriel). |

Une valeur vide (`""`) laisse la valeur par défaut du modèle PDF.

## Annexe 1 – Travail à distance

Le formulaire comporte une page « ANNEXE 1 – Travail à distance » (page 10), qui ne concerne que les personnes en télétravail. Dans Acrobat, ce comportement est piloté par du JavaScript que PyMuPDF n'exécute pas ; le script le reproduit :

- **`travail_distance` = `Oui`** : l'annexe est conservée et son en-tête (nom, poste, service, taux, matricule, dates, motif) est rempli à partir des mêmes données que la page 1. Le bouton « Voir ANNEXE 1 » de la page 1 est affiché.
- **`travail_distance` = `Non`** : la page de l'annexe est supprimée (le PDF passe de 12 à 11 pages) et ses champs sont retirés proprement du formulaire. La page 8 indique « Document annexé « Travail à distance » : non ».

Le nom et le poste de la personne sont aussi repris dans le bloc signatures de la page 8, qui partage ces champs avec l'annexe.

## Description des fichiers

- **`create_ec.py`**: Le script principal qui lit les données du fichier JSON et remplit le formulaire PDF.
- **`AGENTS.md`**: Notes techniques pour les agents de code (et les humains) : pièges de PyMuPDF et du modèle PDF, procédure de vérification.
- **`pyproject.toml`** / **`uv.lock`**: Définition du projet et des dépendances pour uv.
- **`Formulaire_EC_template.pdf`**: Le modèle de formulaire PDF à remplir.
- **`ec_data.json`**: Fichier contenant les données des collaborateurs. Ce fichier, les copies annuelles `ec_data_<année>.json`, le dossier `data/` et les dossiers `ec_outputs*/` sont ignorés par Git pour des raisons de confidentialité.
- **`ec_data_anonymised.json`**: Un exemple de fichier de données avec des informations anonymisées.
- **`list_fields_Pdf.py`**: Un script utilitaire pour lister tous les champs de formulaire d'un PDF, ce qui est très utile pour le mappage des champs.
- **`field_list.txt`**: La sortie du script `list_fields_Pdf.py`, montrant les noms des champs du `Formulaire_EC_template.pdf`.

## Personnalisation

Pour utiliser ce script avec vos propres formulaires PDF, suivez ces étapes :

1.  **Listez les champs de votre PDF** : Utilisez le script `list_fields_Pdf.py` pour obtenir la liste de tous les champs de votre formulaire.
2.  **Mettez à jour le mappage des champs** : Modifiez le dictionnaire `FIELD_MAP` dans `create_ec.py` pour faire correspondre les noms des champs de votre PDF avec les clés de votre fichier JSON.
3.  **Adaptez votre fichier JSON** : Assurez-vous que votre fichier JSON contient les clés et les valeurs correspondantes au nouveau mappage.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
