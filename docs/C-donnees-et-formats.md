# Données et formats

Le RAG traite deux types de sources : des documents texte et des images. Ils
sont tous déposés dans `data/raw/`, mais leur contenu est préparé et indexé
différemment.

## 1. Sources et fichiers produits

| Chemin | Contenu |
|---|---|
| `data/raw/` | Documents texte et images à intégrer |
| `data/processed/documents.jsonl` | Contenu extrait des sources et métadonnées |
| `data/processed/chunks.jsonl` | Passages texte découpés et fiches des images |
| `storage/chroma/` | Vecteurs et métadonnées des collections Chroma |
| `data/generated/` | Images créées par l'outil de génération |
| `output/` | Réponses enregistrées et copies des images utilisées |

L'ingestion parcourt `data/raw/` et ses sous-dossiers. Les fichiers acceptés
sont :

| Type de source | Formats acceptés | Préparation |
|---|---|---|
| Texte | PDF, DOCX, TXT | Extraction et nettoyage du texte |
| Image | PNG, JPG, JPEG, WEBP | Lecture de l'image et collecte de ses caractéristiques ; pas d'OCR |

## 2. Données textuelles

Pour un PDF, le chargeur produit un document par page contenant du texte. Pour
un DOCX ou un TXT, il produit les éléments textuels fournis par le chargeur.
Les caractères nuls et espaces superflus sont nettoyés ; les numéros de page
des PDF commencent à 1 dans les métadonnées.

Chaque enregistrement texte contient :

- `page_content` : le texte extrait ;
- `metadata` : des informations comme `document_id`, `file_path`, `filename`,
  `file_extension` et `media_type: "text"`.

Les documents texte reçoivent aussi `language: "fr"`. Les PDF peuvent avoir
une métadonnée `page` et `source`.

## 3. Données image

Le chargeur ne transforme pas l'image en texte et ne fait pas d'OCR. Il crée
une fiche avec :

- `page_content` vide ;
- les métadonnées communes du fichier et `media_type: "image"` ;
- `image_format`, `image_width`, `image_height`, `image_mode` et
  `file_size_bytes`.

Le fichier image reste à son emplacement source. Le JSONL conserve son chemin
et ses caractéristiques, pas les octets de l'image. Lors de l'indexation,
l'encodeur ouvre ensuite le fichier pour calculer son vecteur visuel. La
recherche par description et la génération d'images sont expliquées dans
[Fonctionnement des images](./F-fonctionnement-des-images.md).

## 4. Format des fichiers intermédiaires

`documents.jsonl` et `chunks.jsonl` sont des fichiers JSONL : chaque ligne
contient un objet JSON autonome avec `page_content` et `metadata`. Les exemples
ci-dessous montrent séparément à quoi ressemble une entrée texte et une entrée
image.

### Exemple d'une entrée texte

Une ligne représentative de `documents.jsonl` :

```json
{"page_content":"Il était une fois...","metadata":{"document_id":"text:conte.pdf","file_path":"data/raw/conte.pdf","filename":"conte.pdf","file_extension":".pdf","media_type":"text","language":"fr","page":1}}
```

Après découpage, `page_content` contient un passage et les métadonnées
comprennent également des informations comme `start_index`, `chunk_id` et
`chunk_length`.

### Exemple d'une entrée image

Une ligne représentative d'une image dans les fichiers intermédiaires :

```json
{"page_content":"","metadata":{"document_id":"image:danse.webp","file_path":"data/raw/danse.webp","filename":"danse.webp","file_extension":".webp","media_type":"image","image_format":"WEBP","image_width":1200,"image_height":800,"image_mode":"RGB","file_size_bytes":85432}}
```

Le contenu reste vide après l'étape de découpage. L'image n'est pas découpée
en passages textuels : cette fiche permet au script d'indexation de reconnaître
le média et de charger l'image depuis `file_path`.
