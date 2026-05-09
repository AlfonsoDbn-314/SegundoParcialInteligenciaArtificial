# Tutor Inteligente de Inteligencia Artificial
## MVP con Arquitectura RAG Hibrida Local y Nube

Proyecto desarrollado como parte del Segundo Parcial de Inteligencia Artificial.
Metodologia: SDD (Spec-Driven Development) | Arquitectura: RAG + Clean/Hexagonal

---

## Descripcion

Agente academico con arquitectura RAG (Retrieval-Augmented Generation) que responde
preguntas de estudiantes ingiriendo fuentes de informacion locales.
El sistema usa un stack hibrido: modelos locales via Ollama con fallback automatico
a la nube via Groq API cuando Ollama no esta disponible.
Los documentos y embeddings nunca salen del equipo local.

---

## Requisitos del Sistema

Opcion A — Ejecucion con Docker (recomendada):
- Docker 20.10 o superior
- Docker Compose v2
- Groq API key gratuita (https://console.groq.com)
- Ollama instalado opccionalmente para modo local

Opcion B — Ejecucion directa con Python:
- Python 3.11 o superior
- Ollama instalado y corriendo (https://ollama.com/download)
- Modelos descargados: llama3.1 y nomic-embed-text
- Groq API key gratuita para fallback en nube

---

## Instalacion y Uso con Docker (Opcion A)

Paso 1 — Clona el repositorio:

    git clone https://github.com/AlfonsoDbn-314/SegundoParcialInteligenciaArtificial.git
    cd SegundoParcialInteligenciaArtificial

Paso 2 — Crea el archivo .env con tu Groq API key:

    echo "GROQ_API_KEY=tu_api_key_aqui" > .env

    Obtener API key gratis en: https://console.groq.com
    Ir a: API Keys > Create key > Copiar el token

Paso 3 — Coloca tus documentos en las carpetas:

    sources/pdf/       para archivos PDF
    sources/prolog/    para archivos .pl
    sources/txt/       para archivos .txt

    El repositorio incluye guia_gitflow.txt como documento de ejemplo.

Paso 4 — Construye y lanza el contenedor:

    docker compose up --build

    La primera vez tarda 3-5 minutos mientras descarga dependencias.
    Las siguientes veces usa: docker compose up

Paso 5 — Indexa los documentos (solo la primera vez):

    docker compose exec tutor-ia python -c "
    from indexer import ChromaDBIndexer
    idx = ChromaDBIndexer()
    idx.index_documents('./sources')
    "

Paso 6 — Abre el navegador en:

    http://localhost:7860

Para detener el contenedor:

    docker compose down

---

## Instalacion y Uso con Python directo (Opcion B)

Paso 1 — Clona el repositorio:

    git clone https://github.com/AlfonsoDbn-314/SegundoParcialInteligenciaArtificial.git
    cd SegundoParcialInteligenciaArtificial

Paso 2 — Crea el entorno virtual:

    python -m venv venv
    source venv/bin/activate        (Linux/Mac)
    venv\Scripts\activate           (Windows)

Paso 3 — Instala las dependencias:

    pip install -r requirements.txt

Paso 4 — Descarga los modelos de Ollama:

    ollama pull llama3.1
    ollama pull nomic-embed-text

Paso 5 — Opcional, configura Groq para fallback:

    echo "GROQ_API_KEY=tu_api_key_aqui" > .env

Paso 6 — Indexa los documentos:

    python -c "
    from indexer import ChromaDBIndexer
    idx = ChromaDBIndexer()
    idx.index_documents('./sources')
    "

Paso 7 — Lanza el tutor:

    python app.py

Paso 8 — Abre el navegador en:

    http://localhost:7860

---

## Agregar Nuevos Documentos

Para agregar nuevos documentos al tutor despues de la instalacion inicial:

Paso 1 — Copia el archivo a la carpeta correspondiente:

    cp mi_documento.pdf sources/pdf/
    cp mis_reglas.pl sources/prolog/
    cp mis_notas.txt sources/txt/

Paso 2 — Re-indexa los documentos:

    Con Docker:
    docker compose exec tutor-ia python -c "
    from indexer import ChromaDBIndexer
    idx = ChromaDBIndexer()
    idx.index_documents('./sources')
    "

    Con Python directo:
    python -c "
    from indexer import ChromaDBIndexer
    idx = ChromaDBIndexer()
    idx.index_documents('./sources')
    "

Paso 3 — El tutor ya puede responder preguntas sobre el nuevo documento.

---

## Estructura del Proyecto

tutor-ia/
├── app.py              — Interfaz Gradio y endpoints FastAPI
├── indexer.py          — Ingestion y vectorizacion de documentos
├── retriever.py        — Consulta RAG y generacion de respuestas
├── router.py           — Enrutador automatico local vs nube
├── models.py           — Entidades del dominio sin dependencias externas
├── interfaces.py       — Contratos abstractos IIndexer, IRetriever, ILLM
├── requirements.txt    — Dependencias del proyecto
├── Dockerfile          — Imagen del contenedor
├── docker-compose.yml  — Orquestacion del contenedor
├── .env                — Variables de entorno (no se sube a GitHub)
├── sources/
│   ├── pdf/            — Guias didacticas en PDF
│   ├── prolog/         — Reglas Prolog (.pl)
│   └── txt/            — Textos planos y tablas de verdad
│       └── guia_gitflow.txt
└── chroma_db/          — Base vectorial local (generada automaticamente)

---

## Logica de Enrutamiento Hibrido

El sistema decide automaticamente que backend usar en cada consulta.

Si Ollama no esta disponible en el host, usa Groq Cloud como fallback.
Si la query supera 300 caracteres, usa Groq Cloud para mejor calidad.
En cualquier otro caso, usa Ollama local con costo cero.

Los documentos y embeddings permanecen siempre en disco local.
Solo el texto de la query viaja a la nube si se activa el fallback.

---

## Seguridad

Deteccion de prompt injection antes de construir el prompt aumentado.
Patrones bloqueados: ignora, olvida, eres ahora, system:, ###, nuevo rol.
ChromaDB y los documentos fuente nunca salen del equipo local.
Las API keys se leen desde variables de entorno, nunca hardcodeadas.
El LLM responde exclusivamente con el contexto recuperado de ChromaDB.

---

## Stack Tecnologico

Lenguaje base: Python 3.11+
Orquestacion RAG: LangChain
LLM Local: Ollama + Llama 3.1
LLM Nube: Groq API con llama-3.1-8b-instant
Embeddings: nomic-embed-text via Ollama
Vector Store: ChromaDB persistente en disco local
Gestion de documentos: PyMuPDF para PDF, lectura nativa para .pl y .txt
Interfaz: Gradio + FastAPI
Contenedor: Docker + Docker Compose

---

## Principios SOLID Aplicados

S — Single Responsibility:
indexer.py tiene una sola responsabilidad: leer, chunkear y persistir documentos.
retriever.py tiene una sola responsabilidad: consultar y generar respuestas.

O — Open/Closed:
Para agregar un nuevo LLM se crea una nueva clase que implementa ILLM.
Los use cases no se modifican.

L — Liskov Substitution:
OllamaLLM y GroqLLM son intercambiables porque ambas implementan ILLM.

I — Interface Segregation:
IIndexer expone solo index_documents().
IRetriever expone solo retrieve().

D — Dependency Inversion:
AskTutorUC recibe IRetriever e ILLM por inyeccion de dependencias.
Nunca instancia ChromaDB ni OllamaLLM directamente.

---

## Documentos Incluidos

guia_gitflow.txt — Guia completa de GitFlow: ramas feature, release y hotfix,
convenciones de commits, reglas de oro y comparacion con Trunk Based Development.

---

## Autor

AlfonsoDbn-314
Segundo Parcial — Inteligencia Artificial
