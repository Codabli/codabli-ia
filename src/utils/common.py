"""utils.py

Fichier commun d'utilitaire au projet.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


def _copy_image(source: Path, target_dir: Path) -> str:
    """
    Copie une image dans un sous-dossier de session.

    Parameters
    ----------
    source : pathlib.Path
        Chemin de l'image à copier.
    target_dir : pathlib.Path
        Dossier de destination (créé si nécessaire).

    Returns
    -------
    str
        Chemin relatif de l'image copiée, depuis le dossier de session.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target_dir / source.name)

    return f"{target_dir.name}/{source.name}"


def _format_source(source: Any) -> str:
    """
    Met en forme une source documentaire pour l'affichage Markdown.

    Parameters
    ----------
    source : str or dict
        Source telle que renvoyée par 'format_context'. Un dictionnaire peut
        contenir 'source' (ou 'file_path', 'title', 'name') et, facultativement,
        'page'.

    Returns
    -------
    str
        Libellé de la source, avec la page si elle est connue.
    """
    if isinstance(source, dict):
        label = (
            source.get("source")
            or source.get("file_path")
            or source.get("title")
            or source.get("name")
            or str(source)
        )
        page = source.get("page")

        return f"{label} (page {page})" if page not in (None, "") else str(label)

    return str(source)


def save_output(
    question: str,
    answer: str,
    tool_results: list,
    sources: list | None = None,
    output_dir: str = "output",
) -> Path:
    """
    Sauvegarde une question, sa réponse, ses sources et les images associées dans un fichier
    Markdown.

    Une arborescence horodatée '<output_dir>/<AAAA-MM-JJ>/<HH-MM-SS>/' est
    créée à chaque appel. Elle contient le fichier 'question_reponse.md' ainsi
    que, selon les cas, un sous-dossier 'search/' (images retrouvées) et un
    sous-dossier 'generated/' (images générées), avec une copie de chaque
    image. Les images sont référencées dans le Markdown par un chemin relatif.
    Une section « Sources » liste les extraits documentaires fournis au LLM,
    si elle n'est pas vide.

    Parameters
    ----------
    question : str
        Texte de la question posée par l'utilisateur.
    answer : str
        Texte de la réponse générée.
    tool_results : list of dict
        Résultats retournés par les outils. Chaque élément contient une clé
        "results" qui est :

        - une liste de dictionnaires avec une clé "metadata" (outil de
          recherche) contenant "media_type" (seule la valeur "image"
          est retenue) et "file_path" ;
        - ou un dictionnaire avec une clé "path" (outil de génération).
    sources : list, default=None
        Sources des extraits documentaires utilisés pour la réponse, telles
        que renvoyées par 'format_context'. Par défaut None (aucune).
    output_dir : str, default="output"
        Dossier racine dans lequel sont enregistrées les sessions.

    Returns
    -------
    pathlib.Path
        Chemin du dossier de session créé ('<output_dir>/<AAAA-MM-JJ>/<HH-MM-SS>').
    """
    now = datetime.now()
    session_dir = Path(output_dir) / now.strftime("%Y-%m-%d") / now.strftime("%H-%M-%S")
    session_dir.mkdir(parents=True, exist_ok=True)

    # Images copiées, par catégorie : liste de chemins relatifs au Markdown
    images: dict[str, list[str]] = {"search": [], "generated": []}
    seen_images = set()

    for tool_result in tool_results:
        results = tool_result.get("results", [])

        # L'outil de génération renvoie un dict, l'outil de recherche une liste
        if isinstance(results, dict):
            results = [results]

        for result in results:
            metadata = result.get("metadata", {})

            if metadata.get("media_type") == "image" and metadata.get("file_path"):
                category, file_path = "search", metadata["file_path"]
            elif result.get("path"):
                category, file_path = "generated", result["path"]
            else:
                continue

            source = Path(file_path)

            if not source.is_file() or str(source) in seen_images:
                continue

            seen_images.add(str(source))
            images[category].append(_copy_image(source, session_dir / category))

    markdown = ["# Question", "", question, "", "# Réponse", "", answer, ""]

    # Sources documentaires (dédoublonnées, ordre conservé)
    formatted_sources = list(dict.fromkeys(_format_source(s) for s in sources or []))

    if formatted_sources:
        markdown.extend(["# Sources", ""])
        markdown.extend(f"- {source}" for source in formatted_sources)
        markdown.append("")

    sections = {
        "search": "# Images retrouvées",
        "generated": "# Images générées",
    }

    for category, title in sections.items():
        if not images[category]:
            continue

        markdown.extend([title, ""])

        for relative_path in images[category]:
            name = Path(relative_path).name
            markdown.extend([f"## {name}", "", f"![{name}]({relative_path})", ""])

    if not seen_images:
        markdown.extend(["# Images", "", "Aucune image retrouvée ou générée."])

    (session_dir / "question_reponse.md").write_text(
        "\n".join(markdown),
        encoding="utf-8",
    )

    return session_dir





def save_conversation(
    conversation: list,
    tool_results: list,
    sources: list | None = None,
    output_dir: str = "output",
) -> Path:

    """Enregistre une conversation au format Markdown avec ses sources et ses images.

    Crée un dossier de session horodaté dans ``output_dir``. Le dossier contient
    un fichier ``conversation.md`` et, si des images sont trouvées, des sous-dossiers
    ``search`` et/ou ``generated`` où celles-ci sont copiées.

    Les images sont recherchées dans les résultats des outils :
    - une image dont les métadonnées indiquent ``media_type == "image"`` est
      classée comme image retrouvée ;
    - un résultat contenant une clé ``path`` est classé comme image générée.

    Les chemins d’images inexistants sont ignorés, et une même image n’est copiée
    qu’une seule fois. Les sources documentaires sont formatées avec
    ``_format_source`` puis dédupliquées.

    Args:
        conversation: Liste des messages de la conversation. Chaque message doit
            contenir les clés ``role`` et ``content``. Les rôles ``user`` et
            ``assistant`` sont ajoutés au document ; les autres rôles sont ignorés.
        tool_results: Résultats des outils ayant éventuellement produit ou trouvé
            des images. Chaque élément peut contenir une clé ``results`` sous
            forme de liste ou de dictionnaire.
        sources: Sources documentaires à ajouter au fichier Markdown. Si la valeur
            est ``None`` ou si la liste est vide, aucune section de sources n’est
            créée.
        output_dir: Répertoire racine dans lequel créer le dossier de session.
            Par défaut, ``"output"``.

    Returns:
        Path: Chemin du dossier de session créé.

    Note:
        Cette fonction suppose que les fonctions ``_copy_image`` et
        ``_format_source`` sont définies ailleurs dans le projet.
    """
    now = datetime.now()

    session_dir = (
        Path(output_dir)
        / now.strftime("%Y-%m-%d")
        / now.strftime("%H-%M-%S")
    )

    session_dir.mkdir(parents=True, exist_ok=True)

    images = {
        "search": [],
        "generated": [],
    }

    seen_images = set()

    # Récupération et copie des images
    for tool_result in tool_results:

        results = tool_result.get("results", [])

        if isinstance(results, dict):
            results = [results]

        for result in results:

            metadata = result.get("metadata", {})

            if (
                metadata.get("media_type") == "image"
                and metadata.get("file_path")
            ):
                category = "search"
                file_path = metadata["file_path"]

            elif result.get("path"):
                category = "generated"
                file_path = result["path"]

            else:
                continue

            source = Path(file_path)

            if not source.is_file():
                continue

            if str(source.resolve()) in seen_images:
                continue

            seen_images.add(str(source.resolve()))

            relative_path = _copy_image(
                source,
                session_dir / category,
            )

            images[category].append(relative_path)

    # Construction du Markdown
    markdown = [
        "<h1>Historique de la conversation</h1>",
        "",
        f"Date : {now.strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        "---",
        "",
    ]

    # Historique des échanges
    for message in conversation:

        role = message["role"]
        content = message["content"]

        if role == "user":
            markdown.extend([
                "<h2>Utilisateur</h2>",
                "",
                content,
                "",
            ])

        elif role == "assistant":
            markdown.extend([
                "<h2>Codabli IA</h2>",
                "",
                content,
                "",
            ])

        markdown.extend(["---", ""])

    # Sources documentaires
    formatted_sources = list(
        dict.fromkeys(
            _format_source(s)
            for s in sources or []
        )
    )

    if formatted_sources:
        markdown.extend([
            "# Sources documentaires",
            "",
        ])

        markdown.extend(
            f"- {source}"
            for source in formatted_sources
        )

        markdown.append("")

    # Images
    sections = {
        "search": "# Images retrouvées",
        "generated": "# Images générées",
    }

    for category, title in sections.items():

        if not images[category]:
            continue

        markdown.extend([title, ""])

        for relative_path in images[category]:

            name = Path(relative_path).name

            markdown.extend([
                f"## {name}",
                "",
                f"![{name}]({relative_path})",
                "",
            ])

    if not seen_images:
        markdown.extend([
            "# Images",
            "",
            "Aucune image retrouvée ou générée.",
        ])

    # Écriture du fichier
    markdown_path = session_dir / "conversation.md"

    markdown_path.write_text(
        "\n".join(markdown),
        encoding="utf-8",
    )

    return session_dir
