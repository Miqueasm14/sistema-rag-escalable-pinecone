"""Pipeline de ingesta: carga los Markdown de /data, los fragmenta y los sube a Pinecone.

Uso: python ingest.py
"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIR, INDEX_NAME, NAMESPACE, get_embeddings
from setup_index import crear_indice_si_no_existe


def _separar_front_matter(texto: str) -> tuple[dict, str]:
    """Lee el bloque '---' inicial de cada Markdown (categoria, modulo) y devuelve (metadatos, cuerpo)."""
    if not texto.startswith("---"):
        return {}, texto
    _, encabezado, cuerpo = texto.split("---", 2)
    metadatos = {}
    for linea in encabezado.strip().splitlines():
        clave, valor = linea.split(":", 1)
        metadatos[clave.strip()] = valor.strip()
    return metadatos, cuerpo.strip()


def cargar_chunks(data_dir: str = DATA_DIR) -> list[Document]:
    """Carga los .md de data_dir y los divide en chunks con metadatos.

    Lo usan la ingesta (para subirlos a Pinecone) y RAGSystem (para armar el
    índice BM25 en memoria, que necesita el texto de los mismos chunks).
    """
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = []
    for ruta in sorted(Path(data_dir).glob("*.md")):
        metadatos, cuerpo = _separar_front_matter(ruta.read_text(encoding="utf-8"))
        for i, texto in enumerate(splitter.split_text(cuerpo)):
            chunks.append(Document(
                page_content=texto,
                metadata={
                    "source": ruta.name,                       # fuente (documento de origen)
                    "categoria": metadatos.get("categoria", "sin-categoria"),
                    "modulo": metadatos.get("modulo", ruta.stem),
                    "chunk_index": i,                          # posición del chunk dentro del documento
                },
            ))
    return chunks


def ingestar() -> None:
    crear_indice_si_no_existe()

    chunks = cargar_chunks()
    documentos = len({c.metadata["source"] for c in chunks})
    print(f"📄 Documentos: {documentos} · ✂️ Chunks: {len(chunks)}")

    # PineconeVectorStore guarda el texto original en metadata["text"] de cada vector:
    # una sola consulta devuelve vector + texto + metadatos, sin una base de datos aparte.
    vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=get_embeddings(), namespace=NAMESPACE)

    # IDs deterministas (archivo + número de chunk): volver a correr la ingesta
    # actualiza los mismos vectores en vez de duplicarlos.
    ids = [f"{c.metadata['source']}-{c.metadata['chunk_index']}" for c in chunks]
    vectorstore.add_documents(chunks, ids=ids)

    print(f"📦 {len(chunks)} chunks subidos al namespace '{NAMESPACE}' del índice '{INDEX_NAME}'")


if __name__ == "__main__":
    ingestar()
