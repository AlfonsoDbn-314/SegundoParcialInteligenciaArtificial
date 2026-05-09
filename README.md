# Tutor Inteligente de Inteligencia Artificial
## MVP con Arquitectura RAG Híbrida (Local + Nube)

Proyecto desarrollado como parte del Segundo Parcial de Inteligencia Artificial.
Metodología: SDD (Spec-Driven Development) | Arquitectura: RAG + Clean/Hexagonal

---

## Descripción

Agente académico con arquitectura RAG (Retrieval-Augmented Generation) que responde
preguntas de estudiantes ingiriendo fuentes de información locales.
El sistema usa un stack híbrido: modelos locales via Ollama con fallback automático
a la nube (Groq API) cuando es necesario. Los documentos y embeddings nunca
salen del equipo local, garantizando privacidad total del material académico.

---

## Stack Tecnológico

Lenguaje base: Python 3.11+
Orquestación RAG: LangChain
LLM Local: Ollama + Llama 3.1 (sin costo, sin red)
LLM Nube: Groq API con Llama 3.1-8b-instant (fallback automático)
Embeddings: nomic-embed-text via Ollama
Vector Store: ChromaDB persistente en disco local
Gestión de documentos: PyMuPDF para PDF, lectura nativa para .pl y .txt
Interfaz: Gradio + FastAPI

---

## Estructura del Proyecto

tutor-ia/
├── app.py              — Interfaz Gradio y endpoints FastAPI
├── indexer.py          — Ingestión y vectorización de documentos
├── retriever.py        — Consulta RAG y generación de respuestas
├── router.py           — Enrutador automático local vs nube
├── models.py           — Entidades del dominio sin dependencias externas
├── interfaces.py       — Contratos abstractos IIndexer, IRetriever, ILLM
├── requirements.txt    — Dependencias del proyecto
├── sources/
│   ├── pdf/            — Guías didácticas en PDF
│   ├── prolog/         — Reglas Prolog (.pl)
│   └── txt/            — Textos planos y tablas de verdad
└── chroma_db/          — Base vectorial local (generada automáticamente)

---

## Requisitos Previos

- Python 3.11 o superior
- Ollama instalado y corriendo (https://ollama.com/download)
- Modelos descargados: llama3.1 y nomic-embed-text
- Opcional: cuenta gratuita en Groq (https://console.groq.com)

---

## Instalación

Paso 1 — Clona el repositorio:

    git clone https://github.com/AlfonsoDbn-314/SegundoParcialInteligenciaArtificial.git
    cd SegundoParcialInteligenciaArtificial

Paso 2 — Crea y activa el entorno virtual:

    python -m venv venv
    source venv/bin/activate        (Linux/Mac)
    venv\Scripts\activate           (Windows)

Paso 3 — Instala las dependencias:

    pip install -r requirements.txt

Paso 4 — Descarga los modelos de Ollama:

    ollama pull llama3.1
    ollama pull nomic-embed-text

Paso 5 — Opcional, configura Groq para fallback en nube:

    echo "GROQ_API_KEY=tu_api_key_aqui" > .env

---

## Uso

Paso 1 — Coloca tus documentos en las carpetas correspondientes:

    sources/pdf/       para archivos PDF
    sources/prolog/    para archivos .pl
    sources/txt/       para archivos .txt

Paso 2 — Indexa los documentos:

    python -c "
    from indexer import ChromaDBIndexer
    idx = ChromaDBIndexer()
    idx.index_documents('./sources')
    "

Paso 3 — Lanza el tutor:

    python app.py

Paso 4 — Abre el navegador en:

    http://localhost:7860

---

## Lógica de Enrutamiento Híbrido

El sistema decide automáticamente qué backend usar en cada consulta:

- Si Ollama no está disponible, usa Groq Cloud como fallback.
- Si la query supera 300 caracteres, usa Groq Cloud para mejor calidad.
- En cualquier otro caso, usa Ollama local con costo cero.

Los documentos y embeddings permanecen siempre en disco local.
Solo el texto de la query y los chunks recuperados viajan a la nube
en caso de activarse el fallback.

---

## Seguridad

El sistema implementa las siguientes medidas de protección:

- Detección de prompt injection antes de construir el prompt aumentado.
- Patrones bloqueados: ignora, olvida, eres ahora, system:, ###, nuevo rol.
- ChromaDB y los documentos fuente nunca salen del equipo local.
- Las API keys se leen desde variables de entorno, nunca hardcodeadas.
- El LLM responde exclusivamente con el contexto recuperado de ChromaDB.

---

## Principios SOLID Aplicados

S — Single Responsibility:
indexer.py tiene una sola responsabilidad: leer, chunkear y persistir documentos.
retriever.py tiene una sola responsabilidad: consultar y generar respuestas.
Ninguno conoce la implementación del otro.

O — Open/Closed:
Para agregar un nuevo LLM se crea una nueva clase que implementa ILLM.
Los use cases AskTutorUC e IndexDocumentsUC no se modifican.

L — Liskov Substitution:
OllamaLLM y GroqLLM son intercambiables en AskTutorUC
porque ambas implementan el contrato de ILLM.

I — Interface Segregation:
IIndexer expone solo index_documents().
IRetriever expone solo retrieve().
Ninguna interfaz obliga a implementar métodos que no corresponden a su rol.

D — Dependency Inversion:
AskTutorUC recibe IRetriever e ILLM por inyección de dependencias.
Nunca instancia ChromaDB ni OllamaLLM directamente.
En tests se pueden pasar MockRetriever y MockLLM sin infraestructura real.

---

## Metodología SDD — Fases Implementadas

sdd-init:
Exploración del repositorio del curso con modelo de ventana extendida (128k tokens).
Genera taxonomía de metadatos y detecta relaciones entre documentos.

sdd-propose:
Definición de arquitectura limpia hexagonal con cuatro capas:
Dominio, Aplicación, Infraestructura e Interfaz.

sdd-spec:
Generación de criterios de aceptación en formato Given/When/Then
con restricciones funcionales y no funcionales documentadas.

sdd-apply:
Generación del código Python del pipeline RAG con codestral-latest.
Produce indexer.py, retriever.py, models.py e interfaces.py.

sdd-verify:
Auditoría del código con modelo de razonamiento extendido.
Detecta alucinaciones del RAG, prompt injection y violaciones SOLID.

---

## Documentos Incluidos

guia_gitflow.txt — Guía completa de GitFlow: ramas feature, release y hotfix,
convenciones de commits, reglas de oro y comparación con Trunk Based Development.

---

## Roadmap

- Soporte para archivos .docx
- Historial de conversación por sesión
- Métricas de Precision@5 en tiempo real
- Migración opcional a Pinecone para despliegue en nube
- Contenedor Docker con docker-compose up

---

## Autor

AlfonsoDbn-314
Segundo Parcial — Inteligencia Artificial
