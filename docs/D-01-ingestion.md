# Ingestion des sources — `01_ingest.py`

Les commandes de cette page se lancent depuis la racine du dépôt.

Déposer les fichiers source acceptés dans `data/raw/`, puis lancer :

```bash
python src/scripts/01_ingest.py
```

Le script charge récursivement les PDF, DOCX, TXT et images pris en charge. Pour
les documents textuels, il extrait le texte, le nettoie et l'associe à des
métadonnées. Pour les images, il enregistre les informations du fichier sans
extraire de texte.

Le résultat est écrit dans `data/processed/documents.jsonl`, avec un document
JSON par ligne. Les chemins peuvent être changés :

```bash
python src/scripts/01_ingest.py --input chemin/vers/sources --output chemin/vers/documents.jsonl
```

Si certains fichiers ne peuvent pas être chargés, le script consigne les erreurs
et poursuit avec les autres. Si aucun contenu exploitable n'est extrait, il
signale une erreur.

Le format des enregistrements texte et image de `documents.jsonl` est présenté
dans [Données et formats](./C-donnees-et-formats.md).
