# Mettre à jour les données du RAG

Cette procédure est à suivre après l'ajout, le remplacement ou le retrait d'un
document dans `data/raw/`.

## Procédure complète

Depuis la racine du dépôt :

```bash
python src/scripts/01_ingest.py
python src/scripts/02_chunk_documents.py
python src/scripts/03_index_documents.py
```

Les étapes doivent être exécutées dans cet ordre : le découpage utilise le
résultat de l'ingestion, et l'indexation utilise le résultat du découpage.

## Vérifier les résultats

1. Vérifier que `data/processed/documents.jsonl` a été actualisé.
2. Vérifier que `data/processed/chunks.jsonl` contient des passages.
3. Vérifier que la commande d'indexation se termine et indique le nombre de
   vecteurs créés.
4. Lancer une recherche ciblée pour confirmer que le nouveau contenu est
   retrouvé :

   ```bash
   python src/scripts/04_search.py "Question sur le nouveau document" --media-types text
   ```

5. Vérifier la réponse complète, si le modèle et son endpoint sont configurés :

   ```bash
   python src/scripts/05_ask.py "Question sur le nouveau document"
   ```

## À savoir avant de relancer l'indexation

Le script d'indexation reconstruit les collections des types de médias présents
dans les données traitées au lieu d'ajouter uniquement les nouveaux documents.
Il faut donc s'attendre au remplacement du contenu de ces collections.

Si un type de média n'est plus présent dans les données (par exemple si toutes
les images ont été retirées), la collection correspondante peut subsister et
contenir des résultats précédents. Vérifier ce cas avant de considérer le
retrait comme appliqué à l'index.

La mise à jour réingère le dossier source complet par défaut. Si un chemin
différent est utilisé, le transmettre à l'étape d'ingestion avec `--input`, puis
passer les fichiers intermédiaires correspondants aux étapes suivantes.

Les réponses précédemment enregistrées sous `output/` ne sont pas supprimées
par cette procédure.
