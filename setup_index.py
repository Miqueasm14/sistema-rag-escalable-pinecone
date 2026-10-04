"""Setup de Pinecone: verifica si el índice existe y lo crea si hace falta (Serverless).

Uso: python setup_index.py
"""

import os

from pinecone import Pinecone, ServerlessSpec

from config import CLOUD, EMBEDDING_DIM, INDEX_NAME, REGION


def crear_indice_si_no_existe():
    """Devuelve el índice de Pinecone, creándolo antes si todavía no existe."""
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

    if pc.has_index(INDEX_NAME):
        descripcion = pc.describe_index(INDEX_NAME)
        if descripcion.dimension != EMBEDDING_DIM:
            raise ValueError(
                f"El índice '{INDEX_NAME}' ya existe con dimensión {descripcion.dimension}, "
                f"pero el modelo de embeddings genera vectores de {EMBEDDING_DIM}. "
                "Usá otro INDEX_NAME o borrá el índice existente."
            )
        print(f"♻️  El índice '{INDEX_NAME}' ya existe — no se vuelve a crear")
    else:
        print(f"🆕 Creando índice Serverless '{INDEX_NAME}' (dimensión {EMBEDDING_DIM}, métrica coseno)...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud=CLOUD, region=REGION),
        )
        print("✅ Índice creado")

    return pc.Index(INDEX_NAME)


if __name__ == "__main__":
    indice = crear_indice_si_no_existe()
    print(indice.describe_index_stats())
