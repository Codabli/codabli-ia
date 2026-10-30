"""rag_chain.py

Module de génération de réponses à partir d'une question et d'un contexte fourni par un index
vectoriel.
"""

from src.generation.llm import create_llm, generate_image
from src.generation.prompt import RAG_PROMPT
from src.retrieval.retriever import load_vector_store, search_documents
from pathlib import Path
from src import config_loader

_config = config_loader.load_config()


def answer_question(question: str, k: int = 4, history: list | None = None, image = False ) -> dict:
    """
    Recherche les documents et génère une réponse fondée sur ceux-ci.

    Parameters
    ----------
    question : str
        Question posée par l'utilisateur.
    k : int, default=4
        Nombre de passages à retourner pour la génération de la réponse.

    Returns
    -------
    dict
        Dictionnaire contenant la question, la réponse générée, les sources utilisées et
        les informations sur l'utilisation des tokens.
    """

    vector_store = load_vector_store()
    results = search_documents(query=question, vector_store=vector_store, k=k)

    context, sources = format_context(results)

    llm = create_llm()
    chain = RAG_PROMPT | llm
    
    
    response = chain.invoke({"question": question, "context": context})
    print(f"response : {response}")
    
    # Métadonnées d'utilisation des tokens renvoyées par le modèle
    usage = response.usage_metadata or {}

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    total_tokens = usage.get("total_tokens")

    print("\n--- UTILISATION DES TOKENS ---")
    print(f"Tokens input  : {input_tokens}")
    print(f"Tokens output : {output_tokens}")
    print(f"Tokens total  : {total_tokens}")
    print("------------------------------\n")


    if image is True:
        img_bytes = generate_image(question)

        output_path = Path(_config["output"]) / _config["generate_image"].format("Paris")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(img_bytes)
    
    return {
        "question": question,
        "answer": response.content,
        "sources": sources,
        "generate_image" : image,
        "token_usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
    }


def format_context(results: list[dict]) -> tuple[str, list[dict]]:
    """
    Formate les passages en extraits identifiables et citables.

    Parameters
    ----------
    results : list[dict]
        Liste de dictionnaires contenant le contenu, les métadonnées et la distance pour chaque
        passage le plus proche de la question.

    Returns
    -------
    tuple[str, list[dict]]
        Une chaîne de caractères représentant le contexte formaté et une liste de dictionnaires
        contenant les informations sur les sources.
    """

    blocks = []
    sources = []

    for index, result in enumerate(results, start=1):
        source_id = f"S{index}"
        metadata = result["metadata"]

        source = {
            "id": source_id,
            "source": metadata.get("source", "Source inconnue"),
            "page": metadata.get("page"),
            "distance": result["distance"],
        }
        sources.append(source)

        blocks.append(
            f"[{source_id}]\n"
            f"Fichier : {source['source']}\n"
            f"Page : {source['page']}\n"
            f"Contenu :\n{result['content']}"
        )

    return "\n\n---\n\n".join(blocks), sources

