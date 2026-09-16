[EIAE-US5] Test de la pédagogie et de la langue (adaptation à l'âge)

Type : Story
Epic : EIA-EVAL Choix du LLM souverain (Module IA « Créer mon Conte Dansé® »)
Composant : R&D IA (spike)
Niveau : Important
Labels : ia, llm, evaluation, pedagogie, langue

DESCRIPTION
En tant qu'équipe de développement, je veux vérifier la qualité pédagogique et linguistique des réponses de chaque modèle (français correct, vocabulaire adapté à la tranche d'âge, ton encourageant), afin de retenir les modèles réellement utilisables avec des enfants.

CONTEXTE
Le CDC insiste sur l'adaptation à l'âge (« âge plutôt que niveau scolaire », de 3-5 à 15-18 ans) et sur un accompagnement bienveillant qui célèbre l'essai plutôt que de corriger sèchement. Un modèle au français approximatif ou au registre inadapté est inutilisable même s'il respecte les consignes de format.

CRITÈRES D'ACCEPTATION

Scénario 1 - Vocabulaire adapté à l'âge
  Etant donné une tranche d'âge 6-8 ans dans le contexte
  Quand on demande une explication (ex. « c'est quoi une péripétie ? »)
  Alors la réponse emploie un vocabulaire simple et des phrases courtes

Scénario 2 - Encouragement
  Etant donné un message de découragement (« on n'y arrive pas »)
  Quand le modèle répond
  Alors il encourage et reformule positivement, sans correction sèche

Scénario 3 - Qualité du français
  Etant donné plusieurs réponses du modèle
  Alors le français est correct (orthographe, grammaire, syntaxe)

Scénario 4 - Sensibilité à l'âge
  Etant donné la même question posée avec deux tranches d'âge différentes
  Alors le niveau de langue s'adapte à la tranche indiquée

SOUS-TÂCHES (à créer dans JIRA)
- Jouer les scénarios de l'axe pédagogie/langue sur tous les candidats.
- Comparer une même question sur 2 tranches d'âge.
- Juger la qualité à l'œil (français, ton, adaptation).

RÈGLES DE GESTION
- RG1 : français incorrect ou registre inadapté = modèle écarté ou déclassé.
- RG2 : l'adaptation à l'âge est pilotée par le contexte injecté ({tranche_age}), à tester réellement.

NOTES TECHNIQUES
- Axe jugé humainement. Attention : certains modèles multilingues « comprennent » le français mais le produisent moins bien.

DÉPENDANCES
- EIAE-US02 (grille + prompt de référence).

DEFINITION OF DONE
[ ] Tous les candidats testés sur l'axe pédagogie/langue
[ ] Verdict par modèle (qualité français + adaptation à l'âge)
