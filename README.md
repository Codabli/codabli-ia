# Codabli IA

Ce dépôt contient le pipeline RAG : préparation de documents texte et image,
indexation dans Chroma, recherche de contenus similaires et génération de
réponses à partir des extraits retrouvés.

La documentation détaillée est dans [`docs/A-README.md`](./docs/A-README.md).
Les préfixes alphabétiques ordonnent les sujets, et les pages `D-01` à `D-05`
suivent les scripts dans leur ordre d'exécution.

## Installation

Python 3.10 ou plus récent est requis. Depuis la racine du dépôt, créer et
activer un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Puis installer les dépendances et le paquet :

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Démarrage rapide du pipeline documentaire

Les commandes s'exécutent depuis la racine du dépôt. Placer d'abord les
documents sources dans `data/raw/`, puis préparer et indexer les données :

```bash
python src/scripts/01_ingest.py
python src/scripts/02_chunk_documents.py
python src/scripts/03_index_documents.py
```

Rechercher un passage sans génération :

```bash
python src/scripts/04_search.py "Votre question"
```

Poser une question au RAG nécessite également la configuration du modèle de
langage dans `.env` :

```bash
python src/scripts/05_ask.py "Votre question"
```


Discussion avec Codabli IA :

```bash
python src/scripts/06_chat.py
```

Les formats source acceptés sont PDF, DOCX, TXT et images PNG, JPG, JPEG ou
WEBP. Attention : l'indexation reconstruit les collections existantes. Voir
[`docs/G-mise-a-jour-des-donnees.md`](./docs/G-mise-a-jour-des-donnees.md)
avant une réindexation.
