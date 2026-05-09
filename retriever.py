import logging
import os
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from models import Query, DocumentChunk, AnswerResponse
from router import LLMRouter, Backend

log = logging.getLogger(__name__)

INJECTION_PATTERNS = [
    "ignora", "olvida", "eres ahora", "system:",
    "###", "instrucciones anteriores", "nuevo rol"
]

PROMPT_TEMPLATE = """Eres un tutor academico de Inteligencia Artificial.
Responde UNICAMENTE con la informacion del contexto proporcionado.
Cita la fuente entre corchetes [fuente, pag.X] despues de cada afirmacion.
Si no encuentras la respuesta di exactamente:
'No encontre esta informacion en el material del curso.'

CONTEXTO:
{context}

PREGUNTA: {query}

RESPUESTA:"""

class TutorRetriever:
    def __init__(self, chroma_path: str = "./chroma_db"):
        self.router = LLMRouter()
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        self.db = Chroma(
            persist_directory=chroma_path,
            embedding_function=self.embeddings,
            collection_name="tutor_ia"
        )

    def _validate_query(self, query: str) -> None:
        lower = query.lower()
        for pattern in INJECTION_PATTERNS:
            if pattern in lower:
                raise ValueError(f"Query bloqueada: patron detectado '{pattern}'")

    def retrieve(self, query: Query, top_k: int = 5) -> list[DocumentChunk]:
        results = self.db.similarity_search_with_score(query.texto, k=top_k)
        return [
            DocumentChunk(
                texto=doc.page_content,
                metadatos=doc.metadata,
                score=float(score)
            )
            for doc, score in results
        ]

    def ask(self, query_text: str) -> AnswerResponse:
        self._validate_query(query_text)
        query = Query(texto=query_text)
        chunks = self.retrieve(query)

        if not chunks:
            return AnswerResponse(
                answer="No encontre esta informacion en el material del curso.",
                sources=[],
                score=0.0
            )

        context = "\n\n".join([
            f"[{c.metadatos.get('fuente','?')}] {c.texto}"
            for c in chunks
        ])
        prompt = PROMPT_TEMPLATE.format(context=context, query=query_text)
        backend = self.router.select_backend(query_text)

        if backend == Backend.LOCAL:
            answer = self._generate_local(prompt)
            backend_name = "ollama/llama3.1"
        else:
            answer = self._generate_cloud(prompt)
            backend_name = "groq/llama3.1"

        sources = list({c.metadatos.get("fuente", "?") for c in chunks})
        avg_score = sum(c.score for c in chunks) / len(chunks)

        return AnswerResponse(
            answer=answer,
            sources=sources,
            score=round(avg_score, 3),
            backend_used=backend_name
        )

    def _generate_local(self, prompt: str) -> str:
        llm = OllamaLLM(
            model="llama3.1",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        return llm.invoke(prompt)

    def _generate_cloud(self, prompt: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            log.warning("GROQ_API_KEY no configurada → usando local")
            return self._generate_local(prompt)
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
