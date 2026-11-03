# Configuration et paramètres

## Variables d'environnement

Le modèle de langage utilisé par les questions-réponses nécessite trois
variables dans un fichier `.env` à la racine du dépôt :

| Variable | Rôle |
|---|---|
| `OVH_AI_ENDPOINTS_ACCESS_TOKEN` | Jeton d'accès à l'API |
| `OVH_AI_ENDPOINTS_MODEL_NAME` | Nom du modèle configuré |
| `OVH_AI_ENDPOINTS_LLAMA=Meta` | Modèle META LLAMA OVH : Meta-Llama-3_3-70B-Instruct |
| `OVH_AI_ENDPOINTS_URL` | URL de l'endpoint de génération de texte |

L'outil de génération d'images attend également :

| Variable | Rôle |
|---|---|
| `OVH_AI_ENDPOINTS_IMAGE_URL` | URL de l'endpoint de génération d'images |

Cette dernière variable n'est pas nécessaire pour lancer les trois étapes de
préparation des documents ni la recherche seule.

Un modèle sans secret est fourni dans `.env.example`. Le fichier `.env` contient
des informations sensibles : ne pas le partager ni le versionner.

## Paramètres de la chaîne

- Le modèle de langage est initialisé dans `src/generation/llm.py`.
- Les noms des collections et des modèles d'embeddings sont définis dans
  `src/constants.py` et dans les scripts concernés.
