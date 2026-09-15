# codabli-ai

Assistant conversationnel basé sur **OVHcloud AI Endpoints**, qui guide un enfant
sur un compte dansé. Le comportement de l'assistant est entièrement piloté par le
fichier `PROMPT.md`.

## Prérequis

- Python 3.10 ou supérieur
- Une clé API OVHcloud AI Endpoints (manager OVHcloud → Public Cloud →
  AI & Machine Learning → AI Endpoints)

## Installation

```bash
git clone <url-du-repo>
cd codabli-ai

python3 -m venv .venvcodabli
source .venvcodabli/bin/activate #Pour Linux
Pour Windows : .venvcodabli\Scripts\activate

pip install -r requirements.txt
```

## Configuration

Copier le fichier `.env.example` en `.env` à la racine du projet :

```
OVH_AI_ENDPOINT_API_KEY=ta_cle_api_ovh
MIS_AI_ENDPOINT_API_KEY=ta_cle_api_mistral
```

Le `.env` est ignoré par git (voir `.gitignore`) et ne doit jamais être commité.
Le modèle vide est versionné sous le nom `.env.example`.

## Utilisation

```bash
python3 essai-qwen.py
```

```bash
python3 essai-mistral.py
```

Le script lit `PROMPT.md` qui est dans `/prompts`, l'envoie comme message système, puis affiche la réponse
du modèle en streaming.

## Structure

```
codabli-ai/
├── essai-qwen.py      # script OVH
├── essai-mistral.py   # script Mistral
├── /prompts/PROMPT.md          # prompt système (le comportement de l'assistant)
├── requirements.txt
├── .gitignore
├── .env               # non versionné
└── README.md
```

## Modèles pour OVH

L'API est compatible OpenAI, base URL :
`https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`

La liste des modèles disponibles s'obtient avec :

```bash
curl https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models \
  -H "Authorization: Bearer $AI_ENDPOINT_API_KEY"
```

## Modèles pour Mistral


Modèles pertinents pour ce projet :

| Modèle | Type | Entrée / Sortie ($/M tokens) |
|---|---|---|
| `Mistral-Small-3.2-24B-Instruct-2506` | instruct | 0.10 / 0.31 |
| `Qwen3.5-9B` | reasoning | 0.12 / 0.18 |


## Notes

- Les modèles **reasoning** (Qwen3.x) émettent une phase de réflexion avant la
  réponse. En streaming, ces tokens arrivent dans `delta.reasoning` et **non**
  dans `delta.content` — une boucle qui ne lit que `content` semble figée alors
  que le modèle répond.
- Le paramètre `chat_template_kwargs.enable_thinking` n'est pas accepté par OVH
  (erreur 400). Pour limiter la réflexion, ajouter `/no_think` en fin de message
  utilisateur, ou utiliser un modèle instruct.
- Toujours définir `timeout` et `max_retries=0` sur le client : sans cela, le SDK
  retente en silence et un blocage devient indétectable.
