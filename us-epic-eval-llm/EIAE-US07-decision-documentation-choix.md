[EIAE-US7] Décision et documentation du choix

Type : Story
Epic : EIA-EVAL Choix du LLM souverain (Module IA « Créer mon Conte Dansé® »)
Composant : R&D IA (spike)
Niveau : Fondamental
Labels : ia, llm, evaluation, decision, souverainete

DESCRIPTION
En tant que chef de projet / CTO, je veux une synthèse comparative des modèles et une recommandation argumentée, afin de trancher le modèle et la plateforme d'inférence et de débloquer l'écriture du backend IA.

CONTEXTE
Aboutissement de l'epic : transformer les tests (US03 à US06) en une décision. Cette décision débloque le point « choix du modèle » de l'epic EIA-0 et conditionne toutes les US backend IA à venir. Elle doit aussi mettre à jour la note souveraineté, aujourd'hui périmée.

CRITÈRES D'ACCEPTATION

Scénario 1 - Synthèse comparative
  Etant donné les résultats des US03 à US06
  Quand on consolide
  Alors on obtient un tableau comparant les candidats sur les 6 axes (conformité, sécurité, pédagogie, latence, coût, tenue du rôle)

Scénario 2 - Recommandation
  Etant donné la synthèse
  Alors une recommandation argumentée est formulée (modèle + plateforme), avec l'arbitrage « modèle français vs hébergement OVH France » explicité

Scénario 3 - Décision tracée
  Etant donné la recommandation
  Quand le chef de projet / CTO tranche
  Alors la décision est consignée (modèle, plateforme, options RGPD : ZDR, DPA zéro entraînement, endpoints UE)

Scénario 4 - Note mise à jour
  Etant donné la décision
  Alors NOTE_DECISION_LLM_SOUVERAIN.md est corrigée (Mistral désormais dispo chez OVH) et reflète la décision

SOUS-TÂCHES (à créer dans JIRA)
- Consolider les résultats des tests en un comparatif unique.
- Rédiger la recommandation et l'arbitrage.
- Faire trancher chef de projet / CTO et consigner la décision.
- Mettre à jour NOTE_DECISION_LLM_SOUVERAIN.md.
- Confirmer les conditions RGPD du fournisseur retenu (ZDR, DPA, localisation).

RÈGLES DE GESTION
- RG1 : la décision doit être tracée et justifiée (pas d'implicite).
- RG2 : la conformité RGPD mineurs (hébergement UE) prime sur l'argument « modèle français ».
- RG3 : la décision est un prérequis à toute US d'implémentation du backend IA.

NOTES TECHNIQUES
- Points à confirmer auprès des fournisseurs : Zero Data Retention Mistral, périmètre SecNumCloud OVH (probablement hors AI Endpoints), clauses DPA/rétention.

DÉPENDANCES
- EIAE-US03, US04, US05, US06.
- Débloque : point « choix du modèle » de l'epic EIA-0 et le futur epic backend IA.

DEFINITION OF DONE
[ ] Comparatif consolidé sur les 6 axes
[ ] Recommandation argumentée + arbitrage souveraineté
[ ] Décision tranchée et consignée (modèle + plateforme + options RGPD)
[ ] NOTE_DECISION_LLM_SOUVERAIN.md mise à jour
