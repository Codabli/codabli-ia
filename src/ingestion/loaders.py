"""loaders.py

Module de chargement et de normalisation des documents depuis le système de fichiers.
"""

import re
from pathlib import Path
from typing import Callable

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from PIL import Image

from src.constants import SUPPORTED_EXTENSIONS, SUPPORTED_EXTENSIONS_IMG, SUPPORTED_EXTENSIONS_TXT
from src.ingestion import LOGGER


def build_common_metadata(file_path: Path, media_type: str) -> dict:
    """
    Construit les métadonnées communes associées à un fichier source.

    Parameters
    ----------
    file_path : Path
        Chemin du fichier dont les métadonnées sont extraites.
    media_type : str
        Type de média du fichier, par exemple "text" ou "image".

    Returns
    -------
    dict
        Métadonnées contenant l'identifiant du document, son chemin, son nom,
        son extension et son type de média.
    """
    return {
        "document_id": f"{media_type}:{file_path.name}",
        "file_path": str(file_path),
        "filename": file_path.name,
        "file_extension": file_path.suffix.lower(),
        "media_type": media_type,
    }


def clean_text(text: str) -> str:
    """
    Nettoie le texte extrait sans supprimer les séparations utiles.

    Parameters
    ----------
    text : str
        Texte à nettoyer.

    Returns
    -------
    str
        Texte nettoyé.
    """
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Supprime les espaces inutiles, mais conserve les paragraphes.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def get_loader(file_path: Path) -> Callable[[Path], list[Document]]:
    """
    Sélectionne la fonction de chargement adaptée à l'extension du fichier.

    Parameters
    ----------
    file_path : Path
        Chemin du fichier dont il faut déterminer le format.

    Returns
    -------
    Callable[[Path], list[Document]]
        Fonction qui charge le fichier et retourne ses documents normalisés.

    Raises
    ------
    ValueError
        Si l'extension du fichier n'est pas prise en charge.
    """
    extension = Path(file_path).suffix.lower()

    if extension in SUPPORTED_EXTENSIONS_TXT:
        return load_text

    elif extension in SUPPORTED_EXTENSIONS_IMG:
        return load_image

    else:
        raise ValueError(f"Extension de fichier non prise en charge : {extension}")


def ingest_directory(directory: str | Path) -> list[Document]:
    """
    Charge récursivement les fichiers pris en charge.

    Parameters
    ----------
    directory : str | Path
        Chemin vers le dossier contenant les fichiers à charger.

    Returns
    -------
    list[Document]
        Liste de documents extraits des fichiers, avec contenu nettoyé et métadonnées enrichies.
    """
    root = Path(directory).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Le dossier documentaire n'existe pas : {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Le chemin n'est pas un dossier : {root}")

    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        LOGGER.warning("Aucun document pris en charge dans %s", root)
        return []

    documents = []
    errors = []
    ignored_count = 0

    for file_path in files:
        relative_path = file_path.relative_to(root).as_posix()
        loader = get_loader(file_path)

        if loader is None:
            ignored_count += 1
            LOGGER.debug("Format ignoré : %s", relative_path)
            continue

        try:
            loaded_documents = loader(file_path)
            documents.extend(loaded_documents)

            LOGGER.info(
                "Chargé : %s (%s élément(s))",
                relative_path,
                len(loaded_documents),
            )

        except Exception as exc:
            errors.append((relative_path, str(exc)))
            LOGGER.exception("Échec du chargement de %s", relative_path)

    LOGGER.info(
        "Bilan : %s fichier(s), %s élément(s), %s fichier(s) ignoré(s), %s erreur(s)",
        len(files),
        len(documents),
        ignored_count,
        len(errors),
    )

    if errors:
        LOGGER.warning("Certains fichiers n'ont pas été chargés :")
        for file_path, error in errors:
            LOGGER.warning("- %s : %s", file_path, error)

    if not documents:
        raise RuntimeError(
            "Aucun contenu exploitable n'a été extrait. "
            "Vérifiez les fichiers et les erreurs du journal."
        )

    return documents


def load_image(file_path: Path) -> list[Document]:
    """
    Charge une image et crée un document contenant ses métadonnées.

    L'image n'est pas convertie en texte ; son document possède un contenu vide
    et des métadonnées décrivant son fichier et ses dimensions.

    Parameters
    ----------
    file_path : Path
        Chemin de l'image à charger.

    Returns
    -------
    list[Document]
        Liste contenant le document associé à l'image.

    Raises
    ------
    OSError
        Si le fichier ne peut pas être ouvert ou lu comme une image.
    """
    metadata = build_common_metadata(file_path, media_type="image")

    with Image.open(file_path) as image:
        image.load()

        metadata.update(
            {
                "image_format": image.format,
                "image_width": image.width,
                "image_height": image.height,
                "image_mode": image.mode,
                "file_size_bytes": file_path.stat().st_size,
            }
        )

    return [Document(page_content="", metadata=metadata)]


def load_text(file_path: Path) -> list[Document]:
    """
    Charge un fichier et normalise son contenu et ses métadonnées.

    Parameters
    ----------
    file_path : Path
        Chemin vers le fichier à charger.

    Returns
    -------
    list[Document]
        Liste de documents extraits du fichier, avec contenu nettoyé et métadonnées enrichies.

    Raises
    ------
    ValueError
        Si le format du fichier n'est pas pris en charge.
    """
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        loader = PyPDFLoader(str(file_path))

    elif extension == ".docx":
        loader = Docx2txtLoader(str(file_path))

    elif extension == ".txt":
        loader = TextLoader(
            str(file_path),
            encoding="utf-8",
            autodetect_encoding=True,
        )

    else:
        raise ValueError(f"Format non pris en charge : {extension}")

    documents = loader.load()
    normalized_documents = []
    common_metadata = build_common_metadata(file_path, media_type="text")

    for page_index, document in enumerate(documents):
        content = clean_text(document.page_content)

        if not content:
            LOGGER.warning(
                "Contenu vide : %s (élément %s)",
                file_path.name,
                page_index,
            )
            continue

        metadata = dict(document.metadata)
        metadata.update(common_metadata)
        metadata["language"] = "fr"

        # PyPDFLoader fournit normalement un numéro de page
        # commençant à zéro : on le convertit en numéro lisible.
        if extension == ".pdf":
            page = metadata.get("page")
            if page is not None:
                metadata["page"] = int(page) + 1

        normalized_documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return normalized_documents
