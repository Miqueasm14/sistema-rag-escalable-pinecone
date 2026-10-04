"""Configuración compartida por todos los scripts del proyecto."""

import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# --- Pinecone ---
INDEX_NAME = os.environ.get("INDEX_NAME", "rag-hibrido-python-docs")
NAMESPACE = "python-stdlib-docs"
CLOUD = "aws"
REGION = "us-east-1"  # región disponible en el plan gratuito de Pinecone Serverless

# --- Embeddings ---
# Se definen en un solo lugar para indexar y consultar siempre con el mismo modelo,
# y para que la dimensión del índice coincida con la del modelo (evita el
# "mismatch de dimensiones": subir vectores de 1536 a un índice de 768, por ejemplo).
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1536

# --- Chunking (en tokens, dentro del rango 500-800 sugerido) ---
DATA_DIR = "data"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

# --- Recuperación ---
TOP_K = 5


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Embeddings de Gemini. Usa GOOGLE_API_KEY del entorno.

    La librería usa automáticamente task_type RETRIEVAL_DOCUMENT al indexar
    y RETRIEVAL_QUERY al consultar.
    """
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, output_dimensionality=EMBEDDING_DIM)
