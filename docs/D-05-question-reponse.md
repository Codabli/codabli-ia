# L'assistant et la question-réponse — `05_ask.py`

Le script `05_ask.py` lance l'assistant. Celui-ci ne fait pas qu'envoyer une
question au modèle de langage : il prépare des sources textuelles, donne au
modèle des consignes et met à sa disposition des outils pour rechercher ou
générer des images.

Le modèle choisit une réponse adaptée à l'intention de la demande. Une question
factuelle, une demande de recherche d'image et une demande de création d'image
ne déclenchent donc pas le même parcours.

## Lancer une question

```bash
python src/scripts/05_ask.py "Votre question"
```

Le modèle de langage doit être configuré dans `.env`. Voir
[Configuration et paramètres](./E-configuration-et-parametres.md).

## Déroulement d'une demande

1. Charger les collections présentes dans `storage/chroma/`.
2. Rechercher automatiquement les trois passages textuels les plus proches de
   la question. Cette recherche a lieu même si la demande porte ensuite sur un
   outil image.
3. Envoyer au modèle la question, les passages trouvés et le prompt système.
4. Le modèle formule une réponse directe ou demande l'exécution d'un outil.
5. Si un outil est demandé, le programme l'exécute et transmet son résultat au
   modèle, qui peut alors rédiger sa réponse finale.
6. Enregistrer la question, la réponse, les références textuelles et les
   images retournées par les outils.

La boucle d'appel au modèle et aux outils est limitée à cinq cycles. La chaîne
met à disposition deux outils : `search_images`, pour retrouver des images déjà
présentes dans la banque, et `generate_image`, pour demander une nouvelle image
à un service externe.

## Comment le modèle utilise les sources

Les extraits retrouvés sont transmis au modèle comme ressources. Le prompt lui
demande de s'appuyer dessus lorsqu'ils sont pertinents, de ne pas inventer de
fait ou de citation venant des sources, et de dire si les extraits ne suffisent
pas à répondre.

Chaque extrait est associé dans le contexte à une référence, au nom du fichier
et à une page si elle est disponible. Les références récupérées sont également
inscrites dans une section « Sources » du fichier `question_reponse.md`.

La recherche retourne jusqu'à trois passages textuels par défaut. Cela ne
garantit pas que les documents contiennent la réponse : la pertinence dépend
des contenus qui ont été ingérés et indexés.

Le modèle reçoit donc à la fois la question et des extraits de référence. Pour
une question simple, il peut répondre en quelques phrases ; pour une question
qui demande une explication ou une vérification de cohérence, il peut expliquer
ce qui pose question et proposer des pistes. Dans tous les cas, le prompt lui
demande de ne pas inventer une information attribuée aux documents.

## Les outils : des actions déclenchées par l'intention

Un *tool* est une action que le programme met à disposition du modèle. Le modèle
peut demander un appel avec des arguments ; le programme exécute alors l'action
réelle et retourne son résultat au modèle. Ce n'est pas le modèle qui parcourt
directement le dossier d'images ni qui appelle les fonctions Python lui-même.

Le prompt impose de ne pas appeler d'outil pour une question factuelle, une
question théorique ou une question sur la cohérence du récit. Pour les images,
il distingue explicitement :

- **retrouver une image existante** : appeler `search_images` ;
- **créer une nouvelle image** : appeler `generate_image`.

Une demande ambiguë du type « une image de forêt » doit être interprétée comme
une recherche dans la banque. Si aucun résultat ne convient, l'assistant peut
proposer ensuite une création. Une simple question sur le récit n'entraîne pas
la recherche d'image, même si une image pourrait être utile : le prompt lui
demande d'abord de proposer cette possibilité et d'attendre l'accord.

Les détails techniques des deux outils et du stockage des images sont dans
[Fonctionnement des images](./F-fonctionnement-des-images.md).

## Exemples de demandes

Les formulations suivantes illustrent le type de parcours prévu. Le texte
exact de la réponse dépend des sources disponibles et du modèle configuré.

| Exemple de question | Parcours attendu | Type de réponse |
|---|---|---|
| « Où se situe le complexe ? » | Recherche automatique dans les passages textuels ; aucun outil image | Réponse factuelle courte si les documents donnent l'information, en indiquant la source. Sinon, l'assistant doit signaler que les extraits ne permettent pas de répondre. |
| « Que veut dire “péripétie” dans notre histoire ? » | Recherche textuelle ; aucun outil image | Explication simple, adaptée à des élèves de 6 à 13 ans, suivie d'une question qui les aide à poursuivre leur récit. |
| « Notre histoire se passe au Moyen Âge, mais un personnage utilise un téléphone. Est-ce cohérent ? » | Recherche textuelle ; aucun outil image | Signaler avec tact ce qui semble incohérent et inviter les élèves à décider s'il s'agit d'un objet magique ou s'ils veulent changer un élément, sans réécrire l'histoire à leur place. |
| « Montre-nous des images de danseurs dans une forêt. » | Appel explicite à `search_images` dans la banque d'images | Présentation brève des images retrouvées ; si aucune image ne convient, l'assistant peut proposer d'en générer une. |
| « Génère une image d'un danseur qui traverse une forêt brumeuse. » | Appel explicite à `generate_image` | Création demandée au service d'images, puis présentation du fichier produit si l'appel réussit. |
| « Une image de forêt pourrait nous aider. » | Pas d'appel immédiat d'outil : le prompt demande de proposer une recherche et d'attendre l'accord | Réponse de suggestion ou question de clarification avant toute recherche. |

Ces exemples couvrent notamment les réponses factuelles sourcées, les
explications pédagogiques, les questions de cohérence, la recherche d'images
existantes et la génération de nouvelles images. Le modèle ajuste son
vocabulaire et la longueur de sa réponse au public visé ; le prompt indique une
tranche d'âge de 6 à 13 ans et demande un langage simple si l'âge précis n'est
pas fourni.

Pour une demande de vocabulaire, par exemple, le résultat attendu est une
explication courte suivie d'une question qui invite les élèves à réutiliser le
mot. Pour une question de cohérence, l'assistant ne corrige pas directement le
récit : il attire l'attention sur l'élément à clarifier et laisse le choix aux
élèves. Pour une recherche ou une création d'image, il ne répond pas seulement
par du texte : l'outil est appelé et les fichiers image peuvent être inclus dans
le résultat Markdown enregistré.

## Consignes données au modèle

Le prompt actif est défini dans `src/generation/prompt.py`. Il demande
notamment des réponses adaptées aux enfants, encourage la création par les
élèves et interdit au modèle d'écrire le conte à leur place.

Les fichiers `prompts/PROMPT.md` et `prompts/conte-danse-ecriture.md` ne sont pas
le prompt injecté dans cette chaîne. Le second est identifié comme un premier
jet et contient des variables de contexte qui ne sont pas alimentées par le
script actuel.

Le script traite une seule question par exécution. Il n'y a pas d'historique de
conversation transmis d'une commande à l'autre : les formulations « comme je
viens de le dire » ou les références à une question précédente ne disposent
donc pas de contexte conservé par cette chaîne.

## Disponibilité des outils image

L'outil de recherche d'images interroge la collection Chroma des images et
retourne au maximum cinq résultats au modèle. Le prompt demande de présenter
au maximum trois images. L'outil de génération, lui, appelle un endpoint
externe.

## Résultats sauvegardés

`src/utils/common.py` crée un dossier horodaté sous
`output/AAAA-MM-JJ/HH-MM-SS/` contenant `question_reponse.md`. Si l'assistant
utilise les outils d'image et que les chemins retournés existent, les images
sont copiées dans des sous-dossiers `search/` ou `generated/` et référencées
dans le Markdown.
