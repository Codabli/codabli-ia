# Indexation vectorielle — `03_index_documents.py`

## Qu'est-ce qu'un embedding ?

Un embedding est une liste de nombres qui représente le contenu d'un texte ou
d'une image. Des éléments proches par leur sens tendent à avoir des vecteurs
proches. Cela permet de retrouver des passages pertinents même si la question
n'emploie pas exactement les mêmes mots que le document.

Les encodeurs normalisent les vecteurs et sont exécutés sur CPU dans le
fonctionnement actuel.

## Modèles utilisés

Les noms sont définis dans `src/constants.py` :

| Usage | Modèle |
|---|---|
| Embeddings des textes | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Embeddings des images | `clip-ViT-B-32` |
| Embeddings des questions destinées à la recherche d'images | `sentence-transformers/clip-ViT-B-32-multilingual-v1` |

Les modèles Sentence Transformers peuvent être téléchargés lors de leur
première utilisation ; une connexion Internet peut donc être nécessaire.

## Collections Chroma

Le script crée des collections distinctes selon le type de média :

- `conte_danse_text` pour les passages textuels ;
- `conte_danse_image` pour les images.

Le préfixe par défaut est `conte_danse`, le répertoire de stockage
`storage/chroma/` et la taille des lots `64`. Le script peut recevoir d'autres
valeurs avec `--collection`, `--persist-dir` et `--batch-size`.

## Lancer l'indexation

Après la préparation des chunks, exécuter :

```bash
python src/scripts/03_index_documents.py
```

Autres chemins et paramètres possibles :

```bash
python src/scripts/03_index_documents.py \
  --input data/processed/chunks.jsonl \
  --persist-dir storage/chroma \
  --collection conte_danse \
  --batch-size 64
```

Le script encode les contenus par lots, puis enregistre les vecteurs, les
contenus et leurs métadonnées dans Chroma. Pour les images, le chemin du fichier
est utilisé pour lire l'image et créer son vecteur.

La préparation des images et le parcours de recherche visuelle sont décrits
dans [Fonctionnement des images](./F-fonctionnement-des-images.md).

## Attention à la reconstruction

Le script de commande appelle actuellement l'indexeur avec `rebuild=True`.
L'indexeur supprime donc les collections existantes concernées avant de les
recréer. Une nouvelle indexation n'est pas une simple addition de documents :
elle remplace le contenu des collections correspondantes.

Seuls les types de médias présents dans le fichier d'entrée sont traités. Si
le fichier ne contient plus aucun élément d'un type (par exemple plus aucune
image), la collection correspondante peut ne pas être supprimée et conserver
des résultats précédents. Le retrait complet d'un type de média doit donc être
vérifié séparément.

Les identifiants persistés sont calculés à partir du contenu et de certaines
métadonnées (source, page, position et chemin). Le `chunk_id` séquentiel ajouté
dans le fichier de chunks sert à identifier un passage dans ce lot ; ce n'est
pas l'identifiant persistant utilisé seul par Chroma.
