# python-fill-pdf-form

### Remplissage Automatisé de formulaire PDF avec Python

Ce projet est un exemple de script Python qui permet de remplir automatiquement des formulaires PDF en utilisant des données structurées au format JSON. C'est une solution idéale pour automatiser la génération de documents répétitifs tels que des formulaires administratifs, des factures, ou des certificats.

## Fonctionnalités

-   **Remplissage de champs de formulaire** : Supporte les champs de texte, les menus déroulants, les cases à cocher et les boutons radio.
-   **Gestion de données externes** : Utilise un fichier JSON pour fournir les données, ce qui facilite la gestion et la mise à jour des informations.
-   **Génération de multiples PDF** : Capable de générer plusieurs documents PDF remplis en une seule exécution, chacun avec ses propres données.
-   **Personnalisable** : Facilement adaptable pour fonctionner avec n'importe quel formulaire PDF.

## Prérequis

Avant de lancer le script, assurez-vous d'avoir Python installé sur votre machine. Vous devrez également installer la bibliothèque `PyMuPDF`.

```bash
pip install PyMuPDF
````

## Utilisation

1.  **Préparez votre modèle PDF** : Placez votre formulaire PDF vierge à la racine du projet et nommez-le `Formulaire_EC_template.pdf`.

2.  **Préparez vos données** : Créez un fichier `ec_data.json` contenant les données à insérer dans le PDF. Vous pouvez vous inspirer du fichier `ec_data_anonymised.json` pour la structure.

3.  **Lancez le script** : Exécutez le script `create_ec.py` depuis votre terminal.

    ```bash
    python create_ec.py
    ```

4.  **Récupérez les PDF générés** : Les nouveaux fichiers PDF remplis seront créés dans le dossier `ec_outputs`.

## Description des fichiers

- **`create_ec.py`**: Le script principal qui lit les données du fichier JSON et remplit le formulaire PDF.
- **`Formulaire_EC_template.pdf`**: Le modèle de formulaire PDF à remplir.
- **`ec_data.json`**: Fichier contenant les données des collaborateurs (ce fichier est ignoré par Git pour des raisons de confidentialité).
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

```
```