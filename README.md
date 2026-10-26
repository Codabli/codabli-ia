# Documentation technique

## Prérequis

- Python 3.10 ou version ultérieure.
- Un environnement virtuel Python.
- Un accès à OVHcloud AI Endpoints pour générer les réponses.
- Un accès Internet lors du premier téléchargement du modèle d'embeddings Hugging Face.

## Installation

Depuis la racine du dépôt, créer et activer un environnement virtuel.

macOS / Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell :

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Installer les dépendances, puis installer le paquet en mode éditable :

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

`requirements.txt` est la source des dépendances de l'application. Le mode éditable
permet d'importer les modules `src` depuis les scripts.

## Configuration

Créer un fichier `.env` à la racine du dépôt :

```dotenv
OVH_AI_ENDPOINTS_ACCESS_TOKEN=votre_token
OVH_AI_ENDPOINTS_MODEL_NAME=nom_du_modele
OVH_AI_ENDPOINTS_URL=https://votre-endpoint.endpoints.kepler.ai.cloud.ovh.net/v1
```

Les trois variables sont requises par `src/generation/llm.py`. Utiliser le nom du
modèle et l'URL d'endpoint fournis par la configuration OVHcloud. Ne pas versionner
le fichier `.env` ni y exposer de token.

## Pipeline documentaire

Ce pipeline prépare les documents pour que l'assistant puisse retrouver les passages
utiles et s'appuyer dessus pour répondre aux questions. Les étapes 1 à 3 préparent
et indexent le contenu ; les étapes 4 et 5 permettent de le consulter.

Placer les documents source dans `data/raw/`. Les formats pris en charge sont
PDF, DOCX et TXT. Les scripts ci-dessous s'exécutent depuis la racine du dépôt.
Les messages des scripts sont affichés dans le terminal et enregistrés dans
`logs/codabli-ia.log`.

### 1. Ingestion

```bash
python src/scripts/01_ingest.py
```

Cette étape extrait le texte des fichiers PDF, DOCX et TXT et y associe des
informations utiles, comme le nom du fichier et le numéro de page. Elle produit
un fichier JSONL normalisé, qui sert d'entrée à l'étape de découpage.

Par défaut, les sources sont lues dans `data/raw/` et le résultat est écrit dans
`data/processed/documents.jsonl`.

Options disponibles :

```bash
python src/scripts/01_ingest.py --input chemin/vers/sources --output chemin/vers/documents.jsonl
```

### 2. Découpage en chunks

```bash
python src/scripts/02_chunk_documents.py
```

Cette étape découpe le texte en passages plus courts, appelés *chunks*, pour
retrouver plus précisément les parties pertinentes lors d'une recherche. Un
chevauchement entre passages aide à conserver le contexte aux frontières de coupe.

Le script lit `data/processed/documents.jsonl` et écrit les chunks dans
`data/processed/chunks.jsonl`. La taille par défaut est de 600 caractères, avec
un chevauchement de 100 caractères.

```bash
python src/scripts/02_chunk_documents.py --chunk-size 600 --chunk-overlap 100
```

Les chemins d'entrée et de sortie peuvent être changés avec `--input` et `--output`.
Le chevauchement doit être inférieur à la taille des chunks.

### 3. Indexation vectorielle

```bash
python src/scripts/03_index_documents.py
```

Cette étape transforme chaque chunk en vecteur numérique (*embedding*) afin que
l'index puisse retrouver des passages proches d'une question par leur sens. Elle
enregistre ces vecteurs dans Chroma, où ils seront consultés par les étapes 4 et 5.

Les chunks sont vectorisés avec
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` et indexés dans
la collection Chroma `conte_danse`, enregistrée dans `storage/chroma/`.
Le modèle d'embeddings est exécuté sur CPU. Le script reconstruit la collection
à chaque exécution.

Options disponibles : `--input`, `--persist-dir`, `--collection`,
`--embedding-model` et `--batch-size`.

### 4. Recherche seule

```bash
python src/scripts/04_search.py "Votre question"
```

Cette étape recherche dans l'index les passages les plus proches d'une question.
Elle affiche les extraits et leurs sources sans demander au modèle de rédiger une réponse ;
elle est notamment utile pour vérifier les résultats de recherche.

Quatre passages sont retournés par défaut. Modifier ce nombre avec `-k` :

```bash
python src/scripts/04_search.py "Votre question" -k 8
```

### 5. Question au RAG

```bash
python src/scripts/05_ask.py "Votre question"
```

Cette étape effectue la recherche de passages pertinents, puis les transmet au
modèle configuré dans `.env` pour qu'il formule une réponse. Elle affiche la réponse
ainsi que les sources utilisées : c'est le parcours complet de question-réponse RAG.

`-k` permet de régler le nombre de passages fournis au modèle :

```bash
python src/scripts/05_ask.py "Votre question" -k 8
```

Après toute modification des documents sources, relancer les étapes d'ingestion,
de découpage et d'indexation pour mettre à jour la collection Chroma.

## Tests et lint

Exécuter les tests :

```bash
python -m pytest -v
```

Vérifier le code avec Ruff :

```bash
ruff check src tests
```

## Arborescence

```text
.
├── archive/                  # Anciens scripts conservés à titre de référence
├── benchmark_LLM/            # Outils de benchmark
├── data/
│   ├── raw/                  # Documents source PDF, DOCX ou TXT
│   └── processed/            # JSONL extraits et découpés
├── src/
│   ├── generation/           # Prompt, client LLM et chaîne RAG
│   ├── ingestion/            # Chargement, découpage et indexation
│   ├── retrieval/            # Chargement de l'index et recherche
│   └── scripts/              # Commandes numérotées du pipeline
├── storage/chroma/           # Index vectoriel persistant
├── tests/                    # Tests automatisés
├── .env                      # Configuration locale, non versionnée
├── pyproject.toml            # Métadonnées de paquet et configuration Ruff
└── requirements.txt          # Dépendances Python
```
