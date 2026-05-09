import logging
import fitz
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from interfaces import IIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s"
)
log = logging.getLogger(__name__)

class ChromaDBIndexer(IIndexer):
    def __init__(self, chroma_path="./chroma_db", collection="tutor_ia"):
        self.chroma_path = chroma_path
        self.collection = collection
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            separators=["\n\n", "\n", ".", " "]
        )

    def index_documents(self, source_dir):
        docs, metadatas = [], []
        path = Path(source_dir)

        for pdf in path.glob("pdf/*.pdf"):
            try:
                chunks, metas = self._parse_pdf(pdf)
                docs.extend(chunks)
                metadatas.extend(metas)
                log.info(f"PDF: {pdf.name} -> {len(chunks)} chunks")
            except Exception as e:
                log.warning(f"Error en {pdf.name}: {e}")

        for pl in path.glob("prolog/*.pl"):
            try:
                chunks, metas = self._parse_prolog(pl)
                docs.extend(chunks)
                metadatas.extend(metas)
                log.info(f"Prolog: {pl.name} -> {len(chunks)} chunks")
            except Exception as e:
                log.warning(f"Error en {pl.name}: {e}")

        for txt in path.glob("txt/*.txt"):
            try:
                chunks, metas = self._parse_txt(txt)
                docs.extend(chunks)
                metadatas.extend(metas)
                log.info(f"TXT: {txt.name} -> {len(chunks)} chunks")
            except Exception as e:
                log.warning(f"Error en {txt.name}: {e}")

        if not docs:
            log.warning("No se encontraron documentos")
            return False

        Chroma.from_texts(
            texts=docs,
            metadatas=metadatas,
            embedding=self.embeddings,
            persist_directory=self.chroma_path,
            collection_name=self.collection
        )
        log.info(f"Total: {len(docs)} chunks indexados")
        return True

    def _parse_pdf(self, path):
        doc = fitz.open(str(path))
        chunks, metas = [], []
        for page in doc:
            text = page.get_text()
            for chunk in self.splitter.split_text(text):
                chunks.append(chunk)
                metas.append({
                    "fuente": path.name,
                    "pagina": page.number + 1,
                    "tipo_doc": "pdf"
                })
        return chunks, metas

    def _parse_prolog(self, path):
        text = path.read_text(encoding="utf-8")
        clauses = [c.strip() for c in text.split(".\n") if c.strip()]
        return clauses, [{"fuente": path.name, "tipo_doc": "prolog"}] * len(clauses)

    def _parse_txt(self, path):
        text = path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return paragraphs, [{"fuente": path.name, "tipo_doc": "txt"}] * len(paragraphs)
