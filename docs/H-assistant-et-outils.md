# Assistant et outils

Cette page explique où l'assistant est défini, comment il utilise ses outils et
comment en ajouter un nouveau.

## Où se trouve l'assistant ?

Les éléments qui composent l'assistant sont regroupés dans `src/generation/`
et `src/tools/` :

| Fichier ou dossier | Rôle |
|---|---|
| `src/generation/chain.py` | Orchestre une demande : recherche les passages texte, appelle le modèle et exécute ses éventuelles demandes d'outils |
| `src/generation/prompt.py` | Définit le rôle, le ton, les consignes et les situations où les outils doivent être utilisés |
| `src/generation/llm.py` | Configure et crée le modèle de langage |
| `src/generation/agent.py` | Assemble et fournit au modèle la liste des outils disponibles |
| `src/tools/` | Contient le code des actions que l'assistant peut demander au programme d'exécuter |

Le parcours est donc réparti : `chain.py` orchestre, `prompt.py` indique au
modèle comment agir, `agent.py` lui présente les outils et chaque module de
`src/tools/` implémente une action.

## Comment fonctionne un outil ?

Un outil (*tool*) est une fonction que le modèle peut demander au programme
d'exécuter. Le modèle ne lance pas lui-même du code : il choisit un outil,
fournit les arguments attendus, puis le programme appelle la fonction et
renvoie son résultat au modèle.

```text
Question
   │
   ▼
Recherche des passages textuels
   │
   ▼
Modèle : réponse directe ou demande d'un outil
   │
   ├── réponse directe ───────────────────► Réponse finale
   │
   └── demande d'outil ► exécution ► résultat transmis au modèle
                                              │
                                              ▼
                                        Réponse finale
```

Dans le parcours actuel, les passages texte sont recherchés avant le premier
appel au modèle. Ensuite, le modèle peut répondre directement ou demander un
outil. Les outils disponibles sont actuellement :

- `search_images` : retrouve des images existantes dans la banque ;
- `generate_image` : demande la création d'une image à un service externe.

Le modèle choisit un outil en fonction de sa description et des règles du
prompt. C'est pourquoi ajouter une fonction dans `src/tools/` ne suffit pas :
elle doit aussi être enregistrée dans `agent.py` et expliquée dans
`prompt.py`.

## Ajouter un outil

### 1. Créer le module de l'outil

Ajouter un fichier dans `src/tools/`, par exemple
`src/tools/example_tool.py`. Un outil suit le modèle des outils existants :
une fabrique retourne une fonction décorée avec `@tool`.
Dans cet exemple, `lookup_information` représente la fonction métier à
implémenter ou à appeler ; ce nom est un espace réservé.

```python
from langchain.tools import BaseTool, tool


def create_example_tool() -> BaseTool:
    @tool
    def example_tool(query: str) -> str:
        """Recherche une information dans le service exemple.

        Args:
            query: Terme à rechercher.
        """
        return lookup_information(query)

    return example_tool
```

Adapter cet exemple à l'action réelle à effectuer :

- choisir un nom d'outil explicite et unique ;
- écrire une description compréhensible par le modèle, car elle l'aide à
  décider quand appeler l'outil ;
- typer les arguments et le résultat pour que les paramètres attendus soient
  clairs ;
- demander seulement les informations nécessaires et valider les entrées
  selon le besoin ;
- retourner un résultat structuré que le modèle peut comprendre. La chaîne le
  convertit en JSON pour le lui transmettre ; les résultats simples
  (texte, nombres, listes et dictionnaires) sont à privilégier ;
- utiliser une fabrique si l'outil a besoin de dépendances déjà créées, comme
  les collections de recherche d'images.

Éviter de mettre des clés d'API ou d'autres secrets dans le code. Pour un
service externe, suivre la configuration par variables d'environnement décrite
dans [Configuration et paramètres](./E-configuration-et-parametres.md).

### 2. Enregistrer l'outil

Importer sa fabrique dans `src/generation/agent.py`, puis l'ajouter à la liste
retournée par `create_assistant_tools` :

```python
from src.tools.example_tool import create_example_tool


def create_assistant_tools(vector_stores):
    return [
        create_image_search_tool(vector_stores),
        create_image_generation_tool(),
        create_example_tool(),
    ]
```

Cette liste est liée au modèle dans `create_assistant` de
`src/generation/chain.py`. La chaîne construit également une table de
correspondance entre le nom de l'outil et sa fonction : le nom retourné par le
modèle doit donc correspondre au nom enregistré.

En général, il n'est pas nécessaire de modifier la boucle d'exécution de
`chain.py` pour un outil qui respecte ce contrat.

### 3. Décrire quand l'utiliser

Modifier `SYSTEM_PROMPT` dans `src/generation/prompt.py` :

1. ajouter l'outil dans la section **OUTILS DISPONIBLES** ;
2. indiquer dans **RÈGLES D'UTILISATION DES OUTILS** les demandes qui doivent
   déclencher l'action et celles qui ne doivent pas la déclencher ;
3. expliquer comment présenter son résultat et quoi dire si aucun résultat
   n'est obtenu ou si l'action échoue.

Exemple de règle à adapter :

```text
- example_tool : recherche une information dans le service exemple.
Utilise cet outil uniquement si l'utilisateur demande explicitement
cette information. Si aucun résultat n'est renvoyé, dis-le clairement.
```

Ne pas ajouter une règle plus large que le comportement réellement souhaité :
le modèle se base sur le nom et les descriptions de l'outil ainsi que sur les
consignes pour décider de l'appeler.

### 4. Prévoir le traitement du résultat

Après l'exécution, `chain.py` renvoie le résultat au modèle. Il ajoute aussi
l'appel et son résultat à `tool_results`, qui est remis au mécanisme de
sauvegarde.

Pour un outil qui retourne du texte ou des données structurées, vérifier que
ce résultat est utile au modèle et sérialisable. Si l'outil retourne un fichier
à afficher ou à conserver, vérifier aussi comment `src/utils/common.py`
enregistre ce type de résultat. Ce module sait actuellement copier les images
reconnues comme images retrouvées ou générées ; un nouveau format de fichier
nécessitera une prise en charge spécifique pour être copié et référencé dans
`question_reponse.md`.

## Points de vigilance

- Le nombre maximal de cycles modèle/outils est limité à cinq.
- Les erreurs d'exécution d'un outil ne sont pas transformées en réponse de
  secours par la chaîne ; vérifier les erreurs et les cas où le service externe
  est indisponible.
- La chaîne traite une question par exécution et ne transmet pas d'historique
  de conversation d'une commande à l'autre.
- Si plusieurs outils peuvent répondre à des demandes voisines, décrire
  clairement dans le prompt la différence entre leurs usages.

Pour les exemples de comportement des outils existants, consulter
[D-05 — Question-réponse](./D-05-question-reponse.md) et
[F — Fonctionnement des images](./F-fonctionnement-des-images.md).

Pour étendre l'index et l'assistant à d'autres médias, consulter
[I — Recherche de vidéos et de musiques](./I-recherche-videos-et-musiques.md).
