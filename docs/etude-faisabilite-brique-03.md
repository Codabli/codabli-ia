# Étude de faisabilité — Brique 03

## 1. Audit et faisabilité des données (Data Audit for RAG)

### Inventaire et formats

L'ingestion accepte les documents PDF, DOCX et TXT, ainsi que les images PNG,
JPG, JPEG et WEBP. Pour les PDF, le texte est extrait page par page. Les
fichiers DOCX et TXT sont chargés comme documents textuels. Les images sont
enregistrées sous forme de fiches de métadonnées (format, dimensions, mode et
taille du fichier) ; leur contenu n'est pas soumis à un OCR.

Les documents textuels comportent le contenu extrait et des métadonnées
d'identification du fichier. Les documents intermédiaires sont enregistrés au
format JSONL.

La répartition réelle du corpus entre contes, fiches pédagogiques,
métadonnées artistiques et éventuelles données de profils n'est pas établie.

### Score de qualité et fiabilité RAG

La qualité des sources peut être évaluée sur un échantillon en vérifiant
l'extraction, la structuration, les doublons, les ambiguïtés et la traçabilité.
La fiabilité RAG peut être mesurée avec un jeu de questions de référence, en
vérifiant si les passages attendus sont retrouvés ; aucun score n'est établi
à ce stade.

### Analyse RGPD et PII

[WORK IN PROGRESS]

## 2. Architecture technique cible et intégration OVHcloud

### Stratégie d'embeddings et Vector Store

Pour le texte, les embeddings sont générés localement sur CPU par
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Pour les
images, le modèle utilisé est `clip-ViT-B-32` ; les requêtes textuelles de
recherche d'images sont encodées par
`sentence-transformers/clip-ViT-B-32-multilingual-v1`.

Les vecteurs sont stockés dans Chroma, avec des collections distinctes pour
le texte et les images et une distance cosinus.

### Pipeline d'ingestion et invalidation

Les fichiers PDF, DOCX et TXT sont extraits en documents textuels ; les
images PNG, JPG, JPEG et WEBP sont conservées sous forme de fiches de
métadonnées. Le texte est nettoyé, puis les documents sont écrits en JSONL.
Le découpage utilise une taille par défaut de 600 caractères et un
chevauchement de 100 caractères. Les embeddings sont calculés localement et
les documents sont indexés dans des collections Chroma distinctes pour le
texte et les images.

Lors d'une réindexation, la collection correspondant à chaque type de média
présent dans les données traitées est supprimée puis recréée. Il n'y a pas de
mise à jour incrémentale par source. Si un type de média n'est plus présent
dans les données traitées, sa collection n'est pas supprimée par cette
réindexation.

### Protocole MCP (Model Context Protocol)

[WORK IN PROGRESS]

## 3. Sécurité et modération Content/PII

### Sécurisation de la chaîne RAG

Le prompt demande des réponses adaptées aux élèves de 6 à 13 ans, interdit à
l'assistant de rédiger le conte à leur place et lui demande de ne pas inventer
de faits attribués aux sources. La chaîne récupère les trois passages
textuels les plus proches et les ajoute au contexte envoyé au modèle.

Aucun composant de modération ni filtre PII avant la recherche ou l'envoi du
contexte au modèle n'est présent dans ce parcours.

### Gestion des accès (RBAC)

Aucun filtrage des documents ou des résultats par rôle n'est effectué dans le
parcours RAG.

## 4. Livrables de la story

### Document d'Architecture Technique (DAT — Brique 03)

[WORK IN PROGRESS]

### Cahier de découpage pour l'implémentation

[WORK IN PROGRESS]

### Chiffrage et estimation des coûts OVHcloud

[WORK IN PROGRESS]
