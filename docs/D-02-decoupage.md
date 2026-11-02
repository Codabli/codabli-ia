# Découpage en passages — `02_chunk_documents.py`

Le découpage transforme les documents préparés par l'ingestion en unités plus
courtes, appelées *chunks*. Les passages facilitent la recherche ciblée : le
RAG peut retrouver une partie pertinente d'un document plutôt que de devoir
transmettre tout le document au modèle.

## Entrée et sortie

Par défaut, le script lit `data/processed/documents.jsonl` et écrit
`data/processed/chunks.jsonl`.

```bash
python src/scripts/02_chunk_documents.py
```

Chaque ligne reste un objet JSON avec `page_content` et `metadata`. Le texte
est découpé ; les métadonnées du document source sont conservées et enrichies
avec la position et les identifiants du chunk.

## Méthode de découpage

Le découpeur cherche des frontières dans cet ordre : paragraphe, ligne, phrase,
espace, puis caractère. La taille par défaut visée est de 600 caractères, avec
un chevauchement de 100 caractères entre deux passages voisins. Le
chevauchement aide à conserver le contexte situé à la frontière entre deux
chunks.

Exemple avec les valeurs par défaut :

```bash
python src/scripts/02_chunk_documents.py \
  --input data/processed/documents.jsonl \
  --output data/processed/chunks.jsonl \
  --chunk-size 600 \
  --chunk-overlap 100
```

Le chevauchement doit être inférieur à la taille du chunk. La taille doit être
strictement positive.

## Traitement des images

Une image a un `page_content` vide : elle n'est pas découpée comme un texte.
Le script la conserve pour que l'étape d'indexation puisse ensuite ouvrir le
fichier image et calculer son embedding visuel. Voir [Fonctionnement des
images](./F-fonctionnement-des-images.md).

## Vérifications faites par le script

Le script vérifie que le fichier d'entrée existe et qu'il contient des
enregistrements exploitables. Il affiche ensuite le nombre de documents et de
chunks, les tailles minimale, maximale et moyenne, ainsi que le fichier de
sortie.
