# Documentation du RAG

Cette documentation décrit comment les documents deviennent consultables et
comment le système utilise les résultats pour répondre à une question.

## Parcours de lecture conseillé

Lisez les pages dans cet ordre pour suivre le fonctionnement du RAG, de ses
sources jusqu'à la réponse. Les préfixes `A` à `I` ordonnent les grands sujets ;
les pages `D-01` à `D-05` suivent l'ordre des scripts.

1. **Comprendre le flux général** : [Vue d'ensemble du RAG](./B-vue-densemble.md)
   présente les étapes et la différence entre préparer les données et répondre
   à une question.
2. **Identifier les données manipulées** : [Données et formats](./C-donnees-et-formats.md)
   décrit les fichiers sources, les formats acceptés et les données
   intermédiaires.
3. **Suivre la préparation des sources** :
   [01 — Ingestion](./D-01-ingestion.md) extrait et normalise le contenu, puis
   [02 — Découpage](./D-02-decoupage.md) transforme les textes en passages.
4. **Comprendre la création de l'index** :
   [03 — Indexation](./D-03-indexation.md) explique les embeddings et les
   collections Chroma.
5. **Comprendre la recherche** : [04 — Recherche](./D-04-recherche.md) explique
   comment une question retrouve des passages ou des images dans l'index.
6. **Préparer les services nécessaires** :
   [Configuration et paramètres](./E-configuration-et-parametres.md) décrit les
   variables et services à configurer avant d'interroger le modèle.
7. **Suivre la réponse complète** :
   [05 — Question-réponse](./D-05-question-reponse.md) décrit le contexte envoyé
   au modèle, ses outils et les fichiers de résultat.
8. **Comprendre les fonctions image** :
   [Fonctionnement des images](./F-fonctionnement-des-images.md) détaille
   l'indexation visuelle, la recherche d'images existantes et leur génération.
9. **Mettre à jour les sources** :
   [Mettre à jour les données](./G-mise-a-jour-des-donnees.md) donne l'ordre des
   commandes à relancer après avoir changé les sources.
10. **Comprendre et étendre l'assistant** :
   [Assistant et outils](./H-assistant-et-outils.md) explique où il est défini,
   comment ses outils fonctionnent et comment en ajouter un.
11. **Ajouter la recherche de vidéos et de musiques** :
   [Recherche de vidéos et de musiques](./I-recherche-videos-et-musiques.md)
   décrit les étapes nécessaires pour étendre la banque de connaissances et
   proposer ces médias depuis l'assistant.

Les commandes sont à lancer depuis la racine du dépôt, dans un environnement
Python où les dépendances du projet sont installées.

## Cheminement du pipeline

`data/raw/` → `01_ingest.py` → `documents.jsonl` → `02_chunk_documents.py` →
`chunks.jsonl` → `03_index_documents.py` → Chroma → `04_search.py` ou
`05_ask.py` → résultats ou réponse.

La recherche d'images suit l'index Chroma image. La génération d'images est un
parcours distinct qui appelle un service externe ; ces deux mécanismes sont
expliqués dans [Fonctionnement des images](./F-fonctionnement-des-images.md).
