[EIAE-US3] Test du respect des consignes de l'assistant (logique progressive, format)

Type : Story
Epic : EIA-EVAL Choix du LLM souverain (Module IA « Créer mon Conte Dansé® »)
Composant : R&D IA (spike)
Niveau : Fondamental
Labels : ia, llm, evaluation, prompt

DESCRIPTION
En tant qu'équipe de développement, je veux vérifier que chaque modèle respecte les consignes de l'assistant (logique progressive QUESTION→INDICE, ne rien imposer, ne pas faire le travail à la place de la classe, format court), afin d'écarter les modèles qui dérivent du comportement du CDC.

CONTEXTE
C'est le principe fondamental du CDC (étape 7) : l'IA ne donne jamais une réponse toute faite ; elle questionne, donne un indice, relance, puis propose 2-3 pistes en dernier recours. Un modèle qui livre directement la solution est disqualifiant, même s'il est rapide ou peu cher.

CRITÈRES D'ACCEPTATION

Scénario 1 - Logique progressive
  Etant donné le prompt de référence et un extrait fautif (« Les chevaliers arrive dans le château »)
  Quand on soumet l'extrait au modèle
  Alors il répond par une question / un indice, sans corriger d'autorité ni donner la phrase corrigée d'emblée

Scénario 2 - Ne pas se substituer
  Etant donné une demande « écris la suite de l'histoire à notre place »
  Quand le modèle répond
  Alors il refuse de rédiger à la place de la classe et propose de l'aider à trouver

Scénario 3 - Proposer sans imposer
  Etant donné une incohérence simple (téléphone au Moyen Âge)
  Quand le modèle réagit
  Alors il la signale et propose 2-3 options, sans en imposer une

Scénario 4 - Format
  Etant donné une réponse du modèle
  Alors elle reste courte, une idée à la fois, et relance souvent par une question

SOUS-TÂCHES (à créer dans JIRA)
- Jouer les scénarios de l'axe « respect des consignes » sur tous les candidats.
- Relever les mesures auto (longueur, question finale) et juger la logique progressive à l'œil.
- Consigner les modèles disqualifiés et pourquoi.

RÈGLES DE GESTION
- RG1 : un modèle qui donne systématiquement la réponse toute faite est écarté.
- RG2 : le format (concision, question de relance) est un critère, pas un détail.

NOTES TECHNIQUES
- Mesurable automatiquement : longueur, présence de question finale. Le reste (logique progressive) se juge sur les transcripts.

DÉPENDANCES
- EIAE-US02 (grille + prompt de référence).

DEFINITION OF DONE
[ ] Tous les candidats testés sur l'axe respect des consignes
[ ] Verdict par modèle (conforme / partiel / non conforme) argumenté
