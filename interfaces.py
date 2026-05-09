from abc import ABC, abstractmethod
from models import Query, DocumentChunk, AnswerResponse

class IIndexer(ABC):
    @abstractmethod
    def index_documents(self, source_dir: str) -> bool:
        pass

class IRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: Query, top_k: int) -> list[DocumentChunk]:
        pass

class ILLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
