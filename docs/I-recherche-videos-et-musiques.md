# Ajouter la recherche de vidéos et de musiques

Cette page décrit les changements nécessaires pour que l'assistant puisse
retrouver et proposer des vidéos ou des musiques de la même façon qu'il peut
aujourd'hui rechercher des images existantes.

## Ce qui existe aujourd'hui

Les outils de l'assistant savent actuellement rechercher des images dans une
collection dédiée ou demander la création d'une image. Les vidéos et les
musiques ne sont pas encore des types de médias pris en charge par le pipeline.

Ajouter seulement un nouvel outil dans `src/tools/` ne suffirait pas :

- l'ingestion ne reconnaît que les textes et les images ;
- l'indexation ne sait créer que les collections `text` et `image` ;
- le chargement et la recherche ne savent ouvrir que ces mêmes collections ;
- la sauvegarde des réponses ne sait recopier et référencer que des images.

Il faut donc créer le parcours complet des médias, de leur préparation à leur
présentation dans la réponse.

## Principe recommandé pour un premier périmètre

Pour proposer des médias à partir d'une demande en langage naturel, le
système doit disposer d'informations compréhensibles par la recherche. Un
fichier audio ou vidéo brut ne contient pas automatiquement une description
exploitable par l'agent.

Un premier périmètre raisonnable consiste à rechercher à partir de :

- une fiche descriptive associée au média : titre, résumé, thème, mots-clés,
  style, durée, langue et public visé ;
- une transcription pour les vidéos parlées et, si elle existe, les paroles
  associées aux musiques ;
- des repères temporels dans ces textes pour retrouver le passage pertinent.

L'assistant renverrait alors le titre, une description, un lien ou chemin vers
le fichier et, si possible, un instant de début et de fin. Il proposerait ainsi
le média sans envoyer le fichier audio ou vidéo complet au modèle de langage.

Pour les vidéos, la recherche par apparence visuelle est une fonction
supplémentaire : elle demande d'extraire des images-clés, de les indexer et de
conserver leur position dans la vidéo. Pour les musiques, retrouver un morceau
à partir d'une description textuelle (par exemple « musique calme avec des
percussions ») s'appuie sur les descriptions et tags. Retrouver un morceau par
ressemblance sonore nécessite en plus une représentation audio adaptée. Ces
deux fonctions ne sont pas fournies par le moteur image actuel.

## Modèle de données à prévoir

Chaque élément indexable doit garder les informations nécessaires pour
retrouver et présenter le média.

### Vidéo

- identifiant stable du média ;
- chemin ou URL de la vidéo ;
- titre et description ;
- tags, thèmes, langue et public ;
- durée ;
- transcription, découpée en segments si elle existe ;
- temps de début et de fin de chaque segment ;
- éventuellement le chemin d'une miniature ou d'une image-clé et son horodatage.

### Musique

- identifiant stable du morceau ;
- chemin ou URL du fichier audio ;
- titre, artiste ou source et durée ;
- tags descriptifs : ambiance, tempo, instruments, style, langue et public ;
- éventuellement paroles ou description textuelle ;
- éventuellement des informations de licence et d'utilisation.

Une transcription, un résumé ou des tags peuvent être rédigés par une personne
ou produits par un traitement dédié. Leur provenance doit être conservée pour
ne pas présenter une description automatique comme une information vérifiée.

Exemple simplifié d'un segment de transcription vidéo :

```json
{
  "page_content": "La danseuse montre un mouvement de rotation.",
  "metadata": {
    "media_type": "video",
    "media_id": "video-001",
    "filename": "mouvement.mp4",
    "file_path": "data/raw/videos/mouvement.mp4",
    "start_seconds": 18.5,
    "end_seconds": 24.0,
    "title": "Découvrir la rotation",
    "language": "fr"
  }
}
```

Exemple simplifié de fiche de musique :

```json
{
  "page_content": "Musique joyeuse et rythmée, avec des percussions.",
  "metadata": {
    "media_type": "audio",
    "media_id": "music-001",
    "filename": "percussions.mp3",
    "file_path": "data/raw/audio/percussions.mp3",
    "duration_seconds": 95,
    "mood": "joyeux",
    "instruments": ["percussions"]
  }
}
```

Ces exemples décrivent une structure à concevoir ; ce ne sont pas des formats
déjà produits par les scripts actuels.

## Changements à prévoir dans le pipeline

### 1. Choisir les sources et formats

Conserver les fichiers dans les dossiers `data/raw/`, avec une fiche de métadonnées par média.

Pour l'extraction d'images-clés ou l'analyse audio, choisir les outils adaptés,
vérifier leurs dépendances et évaluer leur coût de traitement.
Ces opérations ne sont pas nécessaires si les métadonnées et transcriptions sont fournies par
l'équipe.

### 2. Ajouter l'ingestion des médias

Compléter `src/constants.py` et `src/ingestion/loaders.py` pour reconnaître les
nouveaux types et produire des enregistrements normalisés. Pour une vidéo,
l'ingestion pourrait enregistrer le fichier et ses métadonnées ainsi que ses
segments de transcription. Pour une musique, elle pourrait charger sa fiche
descriptive et ses tags.

Les fichiers binaires ne doivent pas être placés dans les JSONL : les
enregistrements contiennent leur chemin, leurs métadonnées et les textes
utilisés pour la recherche.

### 3. Faire circuler ces enregistrements

Adapter `src/ingestion/chunking.py` afin de conserver les nouveaux médias sans
les traiter comme du texte ordinaire. Une transcription peut être découpée en
segments, mais chaque segment doit garder le même identifiant de média et ses
repères temporels. Une fiche descriptive de musique peut rester un seul
enregistrement.

### 4. Créer les index appropriés

Adapter `src/ingestion/indexing.py` pour créer et mettre à jour des collections
séparées, par exemple `conte_danse_video` et `conte_danse_audio`.

Pour un premier périmètre fondé sur les descriptions et transcriptions, les
textes associés à ces médias peuvent être encodés avec un encodeur textuel.
Pour comparer une demande directement à l'apparence d'une vidéo ou au son d'une
musique, il faut en revanche choisir et intégrer des encodeurs multimodaux
spécifiques. Réutiliser l'encodeur image existant ne transforme pas à lui seul
une vidéo ou un fichier audio en vecteur pertinent.

### 5. Étendre le chargement et la recherche

Adapter `src/retrieval/retriever.py` pour :

- ouvrir les nouvelles collections ;
- accepter les nouveaux types de médias ;
- produire un embedding de requête compatible avec chaque collection ;
- retourner les métadonnées nécessaires à la présentation du média ;
- préserver les identifiants, les liens et les repères temporels.

Actuellement, la validation de la recherche n'accepte que `text` et `image`.
Ajouter `video` ou `audio` implique donc de faire évoluer explicitement cette
validation et le chargement des collections.

### 6. Créer un outil de recherche pour chaque usage

Ajouter par exemple :

- `src/tools/video_search.py`, avec un outil `search_videos` ;
- `src/tools/music_search.py`, avec un outil `search_music`.

Chaque outil doit appeler la recherche correspondante et retourner une liste
de résultats structurés : titre, résumé ou extrait, chemin/URL, durée et
repères temporels disponibles. Ne pas retourner le fichier binaire au modèle.

Enregistrer les fabriques dans `create_assistant_tools` de
`src/generation/agent.py`. Le fonctionnement général de cet enregistrement est
décrit dans [Assistant et outils](./H-assistant-et-outils.md).

### 7. Expliquer les outils à l'assistant

Mettre à jour `SYSTEM_PROMPT` dans `src/generation/prompt.py` :

- décrire quand utiliser `search_videos` et `search_music` ;
- différencier une demande de vidéo d'une demande d'image ;
- préciser le nombre maximal de résultats à présenter ;
- demander de communiquer les titres, descriptions et repères temporels utiles ;
- indiquer quoi répondre si aucun résultat n'est trouvé ;
- demander une clarification si l'intention ou les critères sont ambigus.

Exemples de demandes à prendre en charge :

- « Trouve une vidéo qui montre un mouvement de rotation. »
- « Propose une musique joyeuse avec des percussions. »
- « Trouve un morceau calme pour accompagner une scène lente. »

### 8. Présenter et enregistrer les résultats

Les résultats actuels de `04_search.py` sont affichés comme du texte dans les
journaux. `src/utils/common.py` enregistre les images retournées, mais ne sait
pas encore copier ou présenter des fichiers vidéo ou audio.

Définir comment les personnes ouvriront les médias : lien vers le fichier,
chemin accessible, lien web, lecteur intégré dans une future interface, ou
extrait identifié par ses temps de début et de fin. Adapter ensuite la
sauvegarde des réponses pour conserver les références et les métadonnées
nouvelles sans recopier inutilement les médias lourds.

## Étapes de réalisation conseillées

1. Commencer par des fiches descriptives et des transcriptions existantes,
   sans analyse automatique des fichiers audio/vidéo.
2. Créer les enregistrements normalisés avec les chemins et métadonnées.
3. Indexer les textes descriptifs dans des collections audio et vidéo
   distinctes.
4. Ajouter les outils de recherche et les raccorder à l'assistant.
5. Définir comment les résultats seront ouverts et présentés.
6. Vérifier les recherches avec plusieurs formulations et confirmer que les
   liens et temps retournés désignent le bon média.
7. Ajouter ensuite, si le besoin est confirmé, la transcription automatique,
   l'analyse des images-clés vidéo ou la recherche par ressemblance sonore.

Ainsi, la première version peut retrouver une musique ou une vidéo par ce qui
est écrit à son sujet. La recherche par contenu visuel vidéo ou par
ressemblance audio est une évolution séparée, qui nécessite des traitements et
modèles dédiés.
