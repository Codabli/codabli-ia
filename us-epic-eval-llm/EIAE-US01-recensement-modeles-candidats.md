[EIAE-US1] Recensement des modèles candidats (OVH + Mistral)

Type : Story
Epic : EIA-EVAL Choix du LLM souverain (Module IA « Créer mon Conte Dansé® »)
Composant : R&D IA (spike)
Niveau : Fondamental
Labels : ia, llm, evaluation, souverainete

DESCRIPTION
En tant qu'équipe de développement, je veux la liste à jour des modèles de chat disponibles sur OVH AI Endpoints et sur l'API Mistral, avec leur prix, leur taille de contexte et leur lieu d'hébergement, afin de savoir précisément lesquels sont éligibles à l'évaluation.

CONTEXTE
Première brique de l'évaluation : on ne peut pas comparer des modèles sans savoir lesquels existent, à quel prix et hébergés où. Les catalogues bougent (la note souveraineté est déjà périmée : Mistral est désormais présent chez OVH). Ce recensement doit donc être reproductible, pas figé dans un document.

CRITÈRES D'ACCEPTATION

Scénario 1 - Catalogue OVH
  Etant donnée une clé API OVH valide
  Quand on interroge le catalogue OVH AI Endpoints
  Alors on obtient la liste des modèles avec id, prix entrée/sortie et contexte

Scénario 2 - Catalogue Mistral
  Etant donné une clé API Mistral valide
  Quand on interroge l'API Mistral
  Alors on obtient la liste des modèles de chat disponibles pour le compte

Scénario 3 - Filtrage
  Etant donné les deux catalogues
  Quand on constitue la liste des candidats
  Alors on ne retient que les modèles de chat texte (exclusion TTS, embeddings, image, vision seule, modération)

Scénario 4 - Tableau consolidé
  Etant donné la liste filtrée
  Alors chaque candidat indique : fournisseur, id, prix entrée/sortie, contexte, hébergement (UE ?), provenance du modèle (FR / étranger)

SOUS-TÂCHES (à créer dans JIRA)
- Script/commande de listing OVH (endpoint /v1/models).
- Script/commande de listing Mistral (models.list).
- Filtrer les modèles non pertinents.
- Produire le registre consolidé (voir codabli-ai/banc-essai/models.py).

RÈGLES DE GESTION
- RG1 : ne retenir que des modèles dont le traitement est en UE (contrainte souveraineté).
- RG2 : distinguer explicitement provenance du modèle (dimension A) et hébergement (dimension B).
- RG3 : le recensement doit être re-jouable (catalogue évolutif).

NOTES TECHNIQUES
- OVH : API compatible OpenAI, base URL kepler.ai.cloud.ovh.net.
- Le registre codabli-ai/banc-essai/models.py matérialise déjà ce recensement.

DÉPENDANCES
- Clés API OVH et Mistral (codabli-ai/.env).

DEFINITION OF DONE
[ ] Liste des candidats OVH et Mistral obtenue et filtrée
[ ] Prix, contexte, hébergement et provenance documentés pour chaque candidat
[ ] Procédure de rafraîchissement du catalogue documentée
