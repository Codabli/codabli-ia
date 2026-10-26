"""loaders.py

Module de chargement et de normalisation des documents depuis le système de fichiers.
"""

import re
from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document

from src.constants import SUPPORTED_EXTENSIONS
from src.ingestion import LOGGER


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

    for file_path in files:
        try:
            loaded = load_file(file_path)

            # Chemin relatif au corpus, utile pour les sous-dossiers.
            relative_path = str(file_path.relative_to(root))

            for document in loaded:
                document.metadata["source"] = relative_path

            documents.extend(loaded)

            LOGGER.info(
                "Chargé : %s (%s élément(s))",
                relative_path,
                len(loaded),
            )

        except Exception as exc:
            errors.append((str(file_path), str(exc)))
            LOGGER.exception("Échec du chargement de %s", file_path)

    LOGGER.info(
        "Bilan : %s fichier(s), %s élément(s), %s erreur(s)",
        len(files),
        len(documents),
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


def load_file(file_path: Path) -> list[Document]:
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

        # Chemin relatif stable par rapport au dossier data/raw.
        metadata["source"] = file_path.name
        metadata["file_path"] = str(file_path.resolve())
        metadata["file_type"] = extension.lstrip(".")
        metadata["language"] = "fr"

        # PyPDFLoader fournit normalement un numéro de page
        # commençant à zéro : on le convertit en numéro lisible.
        if extension == ".pdf":
            page = metadata.get("page")
            if page is not None:
                metadata["page"] = int(page) + 1

        metadata["document_id"] = str(file_path.resolve())

        normalized_documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return normalized_documents
