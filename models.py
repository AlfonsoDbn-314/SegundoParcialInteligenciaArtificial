from dataclasses import dataclass

@dataclass
class Query:
    texto: str
    max_length: int = 500

    def __post_init__(self):
        if len(self.texto) > self.max_length:
            raise ValueError(f"Query excede {self.max_length} caracteres")

@dataclass
class DocumentChunk:
    texto: str
    metadatos: dict
    score: float = 0.0

@dataclass
class AnswerResponse:
    answer: str
    sources: list[str]
    score: float
    backend_used: str = "local"
