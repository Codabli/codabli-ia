"""constants.py

Module de définition des constantes utilisées dans l'application.
"""

EMBEDDING_MODEL_IMG = "clip-ViT-B-32"
EMBEDDING_MODEL_TXT = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_MODEL_TXT_TO_IMG = "sentence-transformers/clip-ViT-B-32-multilingual-v1"
MAX_EXECUTION_CYCLES_AGENT = 5
SUPPORTED_EXTENSIONS_IMG = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_EXTENSIONS_TXT = {".pdf", ".docx", ".txt"}
SUPPORTED_EXTENSIONS = SUPPORTED_EXTENSIONS_IMG | SUPPORTED_EXTENSIONS_TXT
