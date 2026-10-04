# Sistema RAG escalable en la nube con Pinecone

Módulo de recuperación escalable para un sistema RAG: ingesta de documentos técnicos a un índice **Pinecone Serverless**, un **recuperador híbrido** que combina búsqueda léxica (BM25) con búsqueda vectorial, y un **script de evaluación** que mide Precision@5 y Recall@5 sobre un Golden Set de preguntas.

## Resultados de la evaluación

Salida real de `python evaluate.py` sobre el Golden Set de 5 preguntas:

| Pregunta | Documento esperado | Recall@5 | Precision@5 |
|---|---|---|---|
| ¿Qué hace el parámetro exist_ok de Path.mkdir? | `pathlib.md` | 100% | 60% |
| ¿Cómo evito que json.dumps escape caracteres como la ñ? | `json.md` | 100% | 60% |
| ¿Por qué una segunda llamada a basicConfig no cambia la configuración del logging? | `logging.md` | 100% | 60% |
| ¿Qué estructura conviene para una cola con inserciones y extracciones rápidas en ambos extremos? | `collections.md` | 100% | 60% |
| ¿Qué reemplaza a utcnow desde Python 3.12? | `datetime.md` | 100% | 40% |
| **Promedio** | | **100%** | **56%** |

**Cómo leer estas métricas:**

- **Recall@5**: ¿el documento correcto aparece entre los 5 chunks recuperados? En las 5 preguntas, sí. Vale 0% o 100% por pregunta porque cada una tiene un único documento esperado.
- **Precision@5**: ¿qué proporción de los 5 chunks recuperados viene del documento correcto? Cada documento del dataset se divide en 3 chunks, así que el máximo posible es 3 de 5 = **60%**. El promedio de 56% está a un punto del techo: en 4 de las 5 preguntas el recuperador trajo los 3 chunks del documento correcto.

## Estructura del repositorio

```
sistema-rag-escalable-pinecone/
├── data/                  # Dataset: documentación de 5 módulos de la librería estándar de Python (Markdown)
│   ├── collections.md
│   ├── datetime.md
│   ├── json.md
│   ├── logging.md
│   └── pathlib.md
├── config.py              # Configuración compartida: índice, namespace, embeddings, chunking
├── setup_index.py         # Verifica si el índice existe y lo crea (Serverless)
├── ingest.py              # Pipeline de ingesta: carga, chunking, metadatos y subida a Pinecone
├── rag_system.py          # Clase RAGSystem: EnsembleRetriever (BM25 + Pinecone)
├── evaluate.py            # Precision@5 y Recall@5 sobre el Golden Set
├── golden_set.json        # 5 preguntas con su documento esperado
├── requirements.txt
├── .env.example
└── .gitignore
```

## Cómo funciona

| Componente pedido | Dónde está | Qué hace |
|---|---|---|
| Configuración de variables | `.env` + `config.py` | `PINECONE_API_KEY`, `GOOGLE_API_KEY` e `INDEX_NAME` |
| Setup de Pinecone | `setup_index.py` | Crea el índice Serverless solo si no existe |
| Pipeline de ingesta | `ingest.py` | Markdown → chunks con `RecursiveCharacterTextSplitter` → embeddings → Pinecone |
| Recuperador híbrido | `rag_system.py` → `RAGSystem` | `EnsembleRetriever` que combina BM25 y Pinecone, devuelve el top-5 |
| Evaluación y reporte | `evaluate.py` | Calcula Recall@5 y Precision@5 e imprime el resumen en consola |

### 1. Embeddings y dimensión del índice

Los embeddings se generan con **Gemini** (`gemini-embedding-001`), usando la `GOOGLE_API_KEY` como clave del proveedor (la consigna menciona OpenAI o Anthropic). El modelo se configura con `output_dimensionality=1536`, la misma dimensión que sugiere la consigna para `text-embedding-3-small`.

La dimensión está definida una sola vez, en `config.py` (`EMBEDDING_DIM`), y la usan tanto el modelo de embeddings como la creación del índice. Así se evita el **mismatch de dimensiones**: si el índice ya existe con otra dimensión, `setup_index.py` corta con un error explicativo en lugar de dejar subir vectores incompatibles.

Al indexar, la librería marca los textos como `RETRIEVAL_DOCUMENT`, y al consultar como `RETRIEVAL_QUERY`: Gemini optimiza cada embedding para su rol en la búsqueda.

### 2. Setup del índice (`setup_index.py`)

Verifica con `pc.has_index()` si el índice existe. Si no, lo crea en modo **Serverless** (`aws`, `us-east-1`, la región disponible en el plan gratuito) con métrica coseno. Si ya existe, lo reutiliza.

### 3. Ingesta (`ingest.py`)

- **Dataset:** documentación técnica de 5 módulos de la librería estándar de Python (`pathlib`, `json`, `logging`, `collections`, `datetime`), en Markdown.
- **Chunking:** `RecursiveCharacterTextSplitter.from_tiktoken_encoder` con chunks de **600 tokens** y 100 de solapamiento, dentro del rango de 500 a 800 tokens que recomienda la consigna. Cada documento queda en 3 chunks (15 en total).
- **Metadatos avanzados:** cada chunk lleva `source` (archivo de origen), `categoria` (etiqueta temática, por ejemplo `serializacion` u `observabilidad`), `modulo` y `chunk_index` (posición del chunk dentro del documento, el equivalente a la página para documentos que no son PDF). La categoría y el módulo se leen del encabezado `---` de cada Markdown.
- **Texto en los metadatos:** `PineconeVectorStore` guarda el texto original de cada chunk en `metadata["text"]`. Una sola consulta a Pinecone devuelve el vector, el texto y la fuente, sin necesitar una base de datos aparte.
- **Namespace:** todos los vectores van al namespace `python-stdlib-docs`, separados de cualquier otro dato que se suba al mismo índice.
- **Sin duplicados:** cada vector tiene un ID fijo (`archivo-númerodechunk`, por ejemplo `pathlib.md-0`). Volver a correr la ingesta actualiza los mismos vectores en lugar de duplicarlos.

### 4. Recuperador híbrido (`rag_system.py`)

`RAGSystem` encapsula un `EnsembleRetriever` con dos recuperadores, cada uno con k=5:

- **BM25 (léxico):** busca coincidencias de palabras exactas. Es el que encuentra términos técnicos y nombres propios como `exist_ok`, `basicConfig` o `utcnow`. Se construye en memoria con los mismos chunks que se subieron a Pinecone, y tokeniza en minúsculas y por palabras, para que `"exist_ok?"` o `"¿json.dumps"` coincidan con el texto del documento.
- **Pinecone (semántico):** busca por similitud de embeddings dentro del namespace. Es el que resuelve preguntas que no usan las mismas palabras que el documento, por ejemplo "cola con inserciones en ambos extremos", que encuentra la sección de `deque`.

`EnsembleRetriever` fusiona ambos rankings con Reciprocal Rank Fusion, con pesos 0.5/0.5, y `RAGSystem.buscar(consulta)` devuelve los **top-5** chunks resultantes.

### 5. Evaluación (`evaluate.py`)

Lee las 5 preguntas de `golden_set.json` (pares `pregunta` / `documento_id_esperado`), las pasa por `RAGSystem` y calcula para cada una:

- **Recall@5:** 1 si el documento esperado está entre los 5 recuperados, 0 si no.
- **Precision@5:** cantidad de chunks recuperados que vienen del documento esperado, dividido 5.

Al final imprime el detalle por pregunta y los promedios.

## Cómo replicar el índice y correr la evaluación

Requiere Python 3.12, una cuenta gratuita de [Pinecone](https://app.pinecone.io) y una API key de Gemini (gratis en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).

**1. Entorno virtual y dependencias**

PowerShell (Windows):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno virtual, corré una sola vez:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Git Bash / Linux / macOS:
```bash
python -m venv .venv
source .venv/Scripts/activate    # en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

**2. Variables de entorno**
```bash
cp .env.example .env
# completar PINECONE_API_KEY y GOOGLE_API_KEY con tus keys reales
```

**3. Crear el índice, ingestar y evaluar**
```bash
python setup_index.py    # crea el índice Serverless (si no existe)
python ingest.py         # sube los 15 chunks a Pinecone
python evaluate.py       # imprime Recall@5 y Precision@5
```

Para probar una consulta propia contra el recuperador híbrido:
```bash
python rag_system.py "¿Cómo guardo solo los últimos N eventos?"
```

Después de la ingesta, el índice y sus vectores se ven en la consola web de Pinecone ([app.pinecone.io](https://app.pinecone.io)), dentro del namespace `python-stdlib-docs`.

## Variables de entorno

| Variable | Para qué se usa |
|---|---|
| `PINECONE_API_KEY` | Crear el índice, subir y consultar vectores |
| `GOOGLE_API_KEY` | Generar los embeddings con Gemini |
| `INDEX_NAME` | Nombre del índice de Pinecone (por defecto `rag-hibrido-python-docs`) |

El `.env` está en `.gitignore`: nunca se sube al repositorio.

## Notas

- Al importar `BM25Retriever`, LangChain muestra un aviso de que `langchain-community` dejará de mantenerse. Es solo informativo: el recuperador funciona igual.
- Este proyecto no necesita `torch` (los embeddings se calculan en la API de Gemini), así que corre directamente en Windows, sin WSL.
