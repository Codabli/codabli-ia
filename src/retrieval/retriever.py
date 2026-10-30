"""retriever.py

Module de recherche de documents dans un index vectoriel.
"""

from pathlib import Path

from langchain_chroma import Chroma

from src.ingestion.encoders import BaseEncoder, ImageEncoder, TextEncoder


def load_vector_stores(
    persist_directory: str = "storage/chroma",
    collection_name: str = "conte_danse",
) -> dict[str, Chroma]:
    """
    Charge les collections vectorielles Chroma disponibles.

    Cette fonction initialise les collections Chroma associées aux documents
    textuels et aux images à partir d'un répertoire de persistance.

    Chaque collection est vérifiée afin de déterminer si elle contient
    des vecteurs. Seules les collections non vides sont conservées.

    Les collections sont chargées sans fonction d'embedding, car les
    embeddings des requêtes sont calculés explicitement lors de la recherche
    par les encodeurs TextEncoder et ImageEncoder.

    Parameters
    ----------
    persist_directory : str, default="storage/chroma"
        Chemin du répertoire contenant les données persistantes de Chroma.
    collection_name : str, default="conte_danse"
        Préfixe utilisé pour identifier les collections à charger.

        Les noms des collections recherchées sont :
        - '{collection_name}_text' : collection des documents textuels.
        - '{collection_name}_image' : collection des images.

    Returns
    -------
    dict[str, Chroma]
        Dictionnaire contenant les collections Chroma disponibles et non vides.
        Les clés possibles sont :
        - "text" : collection des documents textuels.
        - "image" : collection des images.
        Les collections absentes ou vides ne sont pas ajoutées au dictionnaire.

    Raises
    ------
    FileNotFoundError
        Si le répertoire contenant l'index vectoriel n'existe pas.
    ValueError
        Si aucune des collections textuelle ou image ne contient de vecteurs.

    Notes
    -----
    Cette fonction suppose que les collections ont déjà été créées lors
    d'une étape précédente d'indexation.

    Les encodeurs ne sont pas initialisés ici afin de limiter le chargement
    des modèles aux seules opérations de recherche.
    """
    persist_path = Path(persist_directory)

    if not persist_path.exists():
        raise FileNotFoundError(
            f"Index introuvable : {persist_path}. Lancez d'abord le script d'indexation."
        )

    stores = {}

    for media_type in ("text", "image"):
        store = Chroma(
            collection_name=f"{collection_name}_{media_type}",
            embedding_function=None,
            persist_directory=str(persist_path),
        )

        if store._collection.count() > 0:
            stores[media_type] = store

    if not stores:
        raise ValueError("Aucune collection texte ou image ne contient de vecteurs.")

    return stores


def search_documents(
    query: str,
    vector_stores: dict[str, Chroma],
    k: int = 4,
    media_types: list[str] | None = None,
) -> list[dict]:
    """
    Recherche des documents similaires à une requête textuelle.

    Cette fonction effectue une recherche sémantique dans les collections
    vectorielles sélectionnées, puis fusionne les résultats obtenus.

    Le fonctionnement se déroule en plusieurs étapes :

    1. Validation de la requête et des paramètres.
    2. Initialisation des encodeurs nécessaires selon les types de médias sélectionnés et les
    collections disponibles.
    3. Encodage de la requête textuelle dans l'espace vectoriel approprié.
    4. Recherche des 'k' documents les plus proches dans chaque collection.
    5. Récupération du contenu, des métadonnées et des distances associées.
    6. Fusion des classements à l'aide de Reciprocal Rank Fusion (RRF).
    7. Tri des résultats selon leur score de fusion.

    La méthode RRF permet de combiner les résultats provenant de modèles
    d'embedding différents sans comparer directement leurs distances.

    Le score de fusion est calculé selon la formule :

    .. math::

        RRF(d) = \\frac{1}{c + rank(d)}

    où 'c' est une constante de classement fixée à 60 et 'rank(d)'
    correspond à la position du document dans sa collection d'origine.

    Parameters
    ----------
    query : str
        Requête textuelle utilisée pour rechercher les documents similaires.
    vector_stores : dict[str, Chroma]
        Dictionnaire des collections Chroma dans lesquelles effectuer
        la recherche.
    k : int, default=4
        Nombre maximum de documents à récupérer dans chaque collection
        avant la fusion des résultats.
    media_types : list[str] | None, default=None
        Types de médias dans lesquels effectuer la recherche.

    Returns
    -------
    list[dict]
        Liste des documents retrouvés, triés par score de fusion décroissant.

        Chaque élément est un dictionnaire contenant les clés suivantes :
        - 'content' : str
            Contenu textuel du document retrouvé. Une chaîne vide est
            retournée si le contenu est absent.
        - 'metadata' : dict
            Métadonnées associées au document. Un dictionnaire vide est
            retourné si les métadonnées sont absentes.
        - 'distance' : float
            Distance vectorielle retournée par Chroma entre la requête
            et le document. Une distance plus faible indique une plus
            grande proximité vectorielle.
        - 'media_type' : str
            Type de média auquel appartient le document ('"text"' ou 'image').
        - 'rank' : int
            Position du document dans les résultats de sa collection
            d'origine, en commençant à 1.
        - 'fusion_score' : float
            Score Reciprocal Rank Fusion calculé à partir du rang du
            document dans sa collection d'origine.

    Raises
    ------
    ValueError
        Si la requête est vide ou ne contient que des espaces.
        Si 'k' est inférieur à 1.
        Si 'media_types' contient un type de média non pris en charge.
    """
    if not query or not query.strip():
        raise ValueError("La question ne doit pas être vide.")

    if k < 1:
        raise ValueError("Le paramètre k doit être supérieur ou égal à 1.")

    if media_types is None:
        media_types = ["text", "image"]

    unsupported = set(media_types) - {"text", "image"}
    if unsupported:
        raise ValueError(f"Types de médias non pris en charge : {unsupported}")

    # Initialiser uniquement les encodeurs nécessaires.
    encoders: dict[str, BaseEncoder] = {}
    if "text" in media_types and "text" in vector_stores:
        encoders["text"] = TextEncoder(device="cpu")

    if "image" in media_types and "image" in vector_stores:
        encoders["image"] = ImageEncoder(device="cpu")

    ranked_results = []
    rrf_constant = 60

    for media_type, encoder in encoders.items():
        store = vector_stores[media_type]

        if media_type == "text":
            query_embedding = encoder.encode([query.strip()])[0]
        else:
            query_embedding = encoder.encode_queries([query.strip()])[0]

        results = store._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for rank, (content, metadata, distance) in enumerate(
            zip(documents, metadatas, distances),
            start=1,
        ):
            ranked_results.append(
                {
                    "content": content or "",
                    "metadata": metadata or {},
                    "distance": float(distance),
                    "media_type": media_type,
                    "rank": rank,
                    "fusion_score": 1 / (rrf_constant + rank),
                }
            )

    # Fusionner les rangs, sans comparer directement les distances.
    ranked_results.sort(
        key=lambda result: result["fusion_score"],
        reverse=True,
    )

    return ranked_results[: k * len(media_types)]
