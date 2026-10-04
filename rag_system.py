"""Recuperador híbrido: combina BM25 (léxico) con búsqueda vectorial en Pinecone (semántico).

Uso: python rag_system.py "tu consulta"
"""

import re
import sys

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

from config import INDEX_NAME, NAMESPACE, TOP_K, get_embeddings
from ingest import cargar_chunks


def _tokenizar(texto: str) -> list[str]:
    # Minúsculas y solo palabras: así "exist_ok?" o "¿json.dumps" coinciden con
    # "exist_ok" y "json.dumps" del documento (el BM25 por defecto separa solo por espacios).
    return re.findall(r"\w+", texto.lower())


class RAGSystem:
    """Encapsula un EnsembleRetriever (BM25 + Pinecone) y devuelve los top-k documentos."""

    def __init__(self, k: int = TOP_K, pesos: tuple[float, float] = (0.5, 0.5)):
        self.k = k

        # Léxico: BM25 sobre los mismos chunks que se subieron a Pinecone.
        # Es bueno con términos exactos (nombres de funciones, parámetros, siglas).
        retriever_bm25 = BM25Retriever.from_documents(cargar_chunks(), preprocess_func=_tokenizar)
        retriever_bm25.k = k

        # Semántico: búsqueda por similitud de vectores en el namespace de Pinecone.
        # Es bueno con parafraseos y preguntas que no usan las palabras del documento.
        vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=get_embeddings(), namespace=NAMESPACE)
        retriever_vectorial = vectorstore.as_retriever(search_kwargs={"k": k})

        # Combina ambos rankings con Reciprocal Rank Fusion, ponderados por `pesos`.
        self.retriever = EnsembleRetriever(
            retrievers=[retriever_bm25, retriever_vectorial],
            weights=list(pesos),
        )

    def buscar(self, consulta: str) -> list[Document]:
        """Devuelve los top-k chunks combinando resultados léxicos y semánticos."""
        return self.retriever.invoke(consulta)[: self.k]


if __name__ == "__main__":
    consulta = " ".join(sys.argv[1:]) or "¿Cómo creo una carpeta solo si no existe?"
    print(f"Consulta: {consulta}\n")
    for i, doc in enumerate(RAGSystem().buscar(consulta), 1):
        meta = doc.metadata
        print(f"{i}. [{meta['source']} · chunk {meta['chunk_index']} · {meta['categoria']}]")
        print(f"   {doc.page_content[:150].strip()}...\n")
