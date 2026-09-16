[EIAE-US2] Grille d'évaluation (scénarios + critères issus du CDC)

Type : Story
Epic : EIA-EVAL Choix du LLM souverain (Module IA « Créer mon Conte Dansé® »)
Composant : R&D IA (spike)
Niveau : Fondamental
Labels : ia, llm, evaluation

DESCRIPTION
En tant qu'équipe de développement, je veux une grille de scénarios de test et de critères, dérivée du comportement attendu de l'assistant (CDC + prompt système de référence), afin d'évaluer tous les modèles à armes égales.

CONTEXTE
Sans grille commune, comparer des modèles revient à des impressions. La grille traduit le CDC (logique progressive, charte « ne pas se substituer », RGPD, adaptation à l'âge) en cas de test concrets, joués à l'identique sur chaque modèle avec le MÊME prompt système de référence.

CRITÈRES D'ACCEPTATION

Scénario 1 - Couverture des axes
  Etant donné le CDC et le prompt de référence
  Quand on constitue la grille
  Alors elle couvre 6 axes : respect des consignes, sécurité/RGPD, pédagogie/langue, comportement technique, coût, tenue du rôle

Scénario 2 - Scénario reproductible
  Etant donné un scénario de test
  Alors il définit le(s) message(s) « classe/élève » et le comportement attendu (grille de jugement)

Scénario 3 - Prompt figé
  Etant donné une campagne d'évaluation
  Quand on lance les tests
  Alors le prompt système de référence est identique pour tous les modèles et versionné

SOUS-TÂCHES (à créer dans JIRA)
- Rédiger le prompt système de référence (fait : codabli-ai/prompts/conte-danse-ecriture.md, premier jet).
- Écrire les scénarios de test (message + attendu) par axe.
- Définir ce qui est mesurable automatiquement vs jugé à l'œil.

RÈGLES DE GESTION
- RG1 : mêmes scénarios et même prompt pour tous les modèles.
- RG2 : chaque scénario est tracé à une règle du CDC (traçabilité).
- RG3 : les axes non mesurables automatiquement (sécurité, pédagogie, tenue du rôle) sont jugés par un humain sur les transcripts.

NOTES TECHNIQUES
- Support existant : codabli-ai/banc-essai/scenarios.py (à réaligner sur le prompt Conte Dansé — les scénarios actuels visent le prototype « prof de danse »).

DÉPENDANCES
- EIAE-US01 (liste des candidats).
- Prompt de référence (conte-danse-ecriture.md).

DEFINITION OF DONE
[ ] Grille couvrant les 6 axes, tracée au CDC
[ ] Prompt système de référence figé et versionné
[ ] Distinction mesures auto / jugement humain explicite
