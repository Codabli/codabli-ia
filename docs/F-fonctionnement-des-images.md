# Fonctionnement des images

Le RAG traite deux familles de contenus, avec des traitements différents :

- **les documents texte**, découpés en passages puis retrouvés à partir de leur
  contenu ;
- **les images**, indexées par leur contenu visuel et retrouvées à partir d'une
  description écrite.

Le système peut aussi appeler un service externe pour générer une nouvelle image.
La recherche dans la banque et la génération sont deux opérations distinctes.

## 1. Constituer la banque d'images

Placer les images dans `data/raw/` ou dans un sous-dossier. Les formats pris en
charge sont PNG, JPG, JPEG et WEBP.

L'ingestion (`src/ingestion/loaders.py`) ne fait pas d'OCR et ne produit pas de
description automatique. Elle vérifie que le fichier est lisible, puis conserve
des informations telles que :

- le chemin et le nom du fichier ;
- son type et son format ;
- sa largeur et sa hauteur ;
- son mode colorimétrique et sa taille en octets.

Dans `documents.jsonl` et `chunks.jsonl`, une image est représentée par un objet
dont le contenu textuel est vide et dont les métadonnées indiquent
`media_type: "image"`. L'image elle-même reste dans son fichier source : ces
fichiers JSONL ne contiennent pas les octets de l'image.

## 2. Transformer les images en vecteurs

Lors de l'indexation, `ImageEncoder` ouvre chaque fichier, le convertit en RGB
et utilise le modèle visuel `clip-ViT-B-32` pour calculer son embedding. Le
vecteur et les métadonnées de l'image sont enregistrés dans la collection
Chroma `conte_danse_image`, dans `storage/chroma/`.

Le contenu textuel envoyé à Chroma pour une image vide est remplacé par son nom
de fichier, ou à défaut par son chemin. Ce libellé ne constitue pas une
description visuelle : la recherche d'image se fonde sur le vecteur visuel.

Pour mettre à jour la banque, suivre les étapes complètes décrites dans
[Mettre à jour les données](./G-mise-a-jour-des-donnees.md). L'indexation
reconstruit la collection image si des images sont présentes dans les données
traitées.

## 3. Retrouver des images à partir d'une demande

La recherche d'image est une recherche **texte-vers-image** :

1. Une demande textuelle, par exemple « une danseuse qui tourne dans une salle
   colorée », est reçue.
2. `ImageEncoder` encode la demande avec
   `sentence-transformers/clip-ViT-B-32-multilingual-v1`.
3. Cet encodeur de requête et l'encodeur visuel produisent des vecteurs dans un
   espace compatible.
4. Chroma compare le vecteur de la demande à ceux des images de
   `conte_danse_image`.
5. L'outil `search_images` retourne au maximum cinq résultats avec leurs
   métadonnées et distances, dont le chemin du fichier source.

Le prompt demande à l'assistant de présenter au maximum trois images, même si
l'outil de recherche peut lui retourner jusqu'à cinq résultats.

Le modèle d'image n'identifie pas nécessairement chaque détail avec certitude :
les résultats sont des images considérées comme proches de la description,
pas une reconnaissance garantie.

### Déclenchement depuis l'assistant

Le prompt dans `src/generation/prompt.py` demande de n'utiliser
`search_images` que si l'utilisateur demande explicitement de retrouver,
d'afficher ou de chercher des images. Une demande de création explicite relève
de l'outil `generate_image`, pas de la recherche.

La commande `04_search.py` peut aussi interroger directement la collection
image :

```bash
python src/scripts/04_search.py "une danseuse qui tourne" --media-types image
```

Cette commande affiche les résultats et leurs métadonnées dans les journaux,
mais ne construit pas à elle seule une galerie d'images. Pour les images, le
script affiche notamment le nom du fichier comme contenu et n'affiche pas
l'image elle-même. Dans le parcours de l'assistant, les fichiers retrouvés
peuvent être copiés dans les résultats enregistrés, comme décrit plus bas.

## 4. Générer une nouvelle image

La génération ne consulte pas la banque d'images. L'outil `generate_image`
envoie une description au service configuré par `OVH_AI_ENDPOINTS_IMAGE_URL`,
avec le modèle `stable-diffusion-xl-base-v10`. Le service renvoie le contenu
binaire de l'image, que le programme écrit sous `data/generated/` avec un nom
horodaté en `.png`.

Le prompt système prévoit que l'assistant n'appelle cet outil qu'à la demande
explicite de création, et qu'il construise la description à partir des idées
fournies, sans ajouter de nouveaux éléments d'intrigue.

## 5. Où vont les images des réponses ?

Après l'échange avec le modèle, `src/utils/common.py` examine les résultats
d'outils :

- une image retrouvée est copiée depuis son `file_path` source dans le dossier
  de session `output/AAAA-MM-JJ/HH-MM-SS/search/` ;
- une image générée est copiée depuis `data/generated/` dans
  `output/AAAA-MM-JJ/HH-MM-SS/generated/`.

Le fichier `question_reponse.md` de la session contient des liens Markdown
relatifs vers les images copiées. Le fichier image généré original reste aussi
dans `data/generated/`. Le code ignore une image si le chemin retourné n'existe
pas ou ne pointe pas vers un fichier.

## Résumé des parcours

| Besoin | Parcours | Résultat |
|---|---|---|
| Retrouver une image existante | Texte de la demande → embedding de requête → collection `conte_danse_image` → chemins des images proches | Images référencées dans les résultats ; copie dans `output/.../search/` pour le parcours assistant |
| Créer une nouvelle image | Description → endpoint configuré → modèle `stable-diffusion-xl-base-v10` | Fichier PNG dans `data/generated/`, puis copie dans `output/.../generated/` |
