EPIC EIA-EVAL — Choix du LLM souverain (évaluation des modèles candidats)

Type : Epic
Initiative : Module IA « Créer mon Conte Dansé® » (Codabli, Annexe 6 - CDC fonctionnel)
Composant : R&D IA (spike) — préalable au backend IA
Labels : ia, llm, evaluation, souverainete

OBJECTIF
Choisir, de façon étayée, le modèle et la plateforme d'inférence (OVH AI Endpoints / API Mistral) AVANT d'écrire le backend IA. On éprouve les modèles candidats sur le comportement réellement attendu de l'assistant (CDC + prompt système de référence) et sur les contraintes du projet : RGPD mineurs, souveraineté, budget, latence. La sortie de cet epic est une décision documentée qui débloque le point « choix du modèle » de l'epic EIA-0.

PÉRIMÈTRE (User Stories)
- EIAE-US01 : Recensement des modèles candidats (OVH + Mistral)
- EIAE-US02 : Grille d'évaluation (scénarios + critères issus du CDC)
- EIAE-US03 : Test du respect des consignes de l'assistant (logique progressive, format)
- EIAE-US04 : Test des garde-fous de sécurité et RGPD
- EIAE-US05 : Test de la pédagogie et de la langue (adaptation à l'âge)
- EIAE-US06 : Mesure de la latence, du coût et du comportement technique
- EIAE-US07 : Décision et documentation du choix

HORS PÉRIMÈTRE (traité ailleurs)
- L'implémentation du backend IA (passerelle, endpoint de conversation, persistance) : vient APRÈS la décision.
- Le contenu pédagogique de chaque étape du parcours : voir EIA-1 à EIA-7.

CONTRAINTES TRANSVERSES (rappel CDC + schéma IA_fondamentale)
- Souveraineté : hébergement / traitement UE, pas de Cloud Act.
- RGPD mineurs (niveau Critique) : minimisation, zéro rétention, zéro entraînement, suppression.
- Budget associatif serré (~4 000 € R&D / ~14 200 € an 1).
- L'IA accompagne, elle ne se substitue jamais aux élèves (Fondamental).
- Tranches d'âge visées : 3-5 à 15-18 ans (CDC), cœur 6-12.

POINTS À TRANCHER (bloquants)
- Arbitrage produit : privilégier le « modèle français » (Mistral) ou l'« hébergement OVH France » ? (cf. NOTE_DECISION_LLM_SOUVERAIN.md — les deux dimensions sont indépendantes).
- ⚠️ La note souveraineté est périmée sur un point : des modèles Mistral SONT désormais au catalogue OVH (Mistral-Small-3.2-24B, Mistral-7B, Mistral-Nemo) — l'option « modèle français + hébergé OVH France » n'est plus impossible. À corriger avant la décision (US07).

DÉPENDANCES
- Prompt système de référence : codabli-ai/prompts/conte-danse-ecriture.md (premier jet).
- Clés API OVH et Mistral (codabli-ai/.env).
- Banc d'essai existant : codabli-ai/banc-essai/ (support d'exécution des US02 à US06).
