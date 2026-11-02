# Recherche dans l'index — `04_search.py`

## Recherche sans génération

Pour rechercher des passages sans appeler le modèle de langage :

```bash
python src/scripts/04_search.py "Votre question"
```

Ce script interroge directement l'index et affiche les résultats dans les
journaux. Il n'appelle pas le modèle de langage et ne rédige pas de réponse.

Par défaut, la recherche demande jusqu'à 4 résultats par type de média. Le
nombre peut être modifié avec `-k`. Les types peuvent être limités à `text`,
`image`, ou aux deux :

```bash
python src/scripts/04_search.py "Votre question" -k 8 --media-types text
```

Le moteur encode la question avec l'encodeur correspondant à chaque collection,
puis demande à Chroma les voisins les plus proches. Quand plusieurs types de
médias sont interrogés, leurs classements sont combinés par Reciprocal Rank
Fusion (RRF). Cette méthode combine les rangs, et non les distances brutes de
modèles différents. La recherche retourne jusqu'à `k` résultats par type
sélectionné.

Le parcours de question-réponse et les appels aux outils de l'assistant sont
décrits dans [Question-réponse avec le RAG](./D-05-question-reponse.md). Pour les
détails de recherche d'images, voir [Fonctionnement des images](./F-fonctionnement-des-images.md).
