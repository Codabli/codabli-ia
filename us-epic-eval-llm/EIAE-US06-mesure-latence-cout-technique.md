[EIAE-US6] Mesure de la latence, du coût et du comportement technique

Type : Story
Epic : EIA-EVAL Choix du LLM souverain (Module IA « Créer mon Conte Dansé® »)
Composant : R&D IA (spike)
Niveau : Important
Labels : ia, llm, evaluation, cout, performance

DESCRIPTION
En tant qu'équipe de développement, je veux mesurer la latence, le coût et le comportement technique de chaque modèle, afin de vérifier la tenue du budget (~14 200 €/an) et une expérience temps réel acceptable en classe.

CONTEXTE
Un modèle peut être excellent pédagogiquement mais trop lent (mode Classe au vidéoprojecteur) ou trop cher pour un budget associatif. Les modèles reasoning (Qwen3.x) réfléchissent avant de répondre : il faut mesurer la latence sur le premier token de contenu (ce que l'utilisateur ressent), pas sur le début de la réflexion.

CRITÈRES D'ACCEPTATION

Scénario 1 - Latence
  Given un scénario de test
  When on interroge un modèle en streaming
  Then on mesure le temps jusqu'au premier token de contenu et la durée totale

Scénario 2 - Coût réel
  Given un échange
  Then on relève les tokens entrée/sortie et on calcule le coût, extrapolé à un volume type (ex. 1000 échanges)

Scénario 3 - Modèles reasoning
  Given un modèle reasoning
  When il répond
  Then on distingue les tokens de réflexion des tokens de contenu et on note l'impact sur la latence

Scénario 4 - Robustesse
  Given un appel qui échoue ou dépasse le délai
  Then l'échec est visible et n'interrompt pas la campagne (timeout explicite, pas de retry silencieux)

SOUS-TÂCHES (à créer dans JIRA)
- Instrumenter les appels (latence 1er token, durée, tokens, coût).
- Extrapoler le coût à un volume type et le rapprocher du budget.
- Consigner le comportement des modèles reasoning (streaming, /no_think).

RÈGLES DE GESTION
- RG1 : mesurer la latence sur le premier token de CONTENU.
- RG2 : timeout explicite et max_retries=0 (un blocage doit être détectable).
- RG3 : le coût est un critère de sélection au même titre que la qualité.

NOTES TECHNIQUES
- Support existant : codabli-ai/banc-essai/ (mesure déjà latence, tokens, coût et sépare les tokens reasoning).
- Prix API Mistral à reconfirmer ; prix OVH relevés au catalogue live.

DÉPENDANCES
- EIAE-US01 (prix des candidats), EIAE-US02 (scénarios).

DEFINITION OF DONE
[ ] Latence, coût et comportement technique mesurés pour tous les candidats
[ ] Coût extrapolé rapproché du budget
[ ] Comportement des modèles reasoning documenté
