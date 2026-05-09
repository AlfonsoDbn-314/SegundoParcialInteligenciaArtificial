import requests
import os
from enum import Enum
from dataclasses import dataclass

class Backend(Enum):
    LOCAL = "local"
    CLOUD = "cloud"

@dataclass
class RouterConfig:
    ollama_url: str = "http://localhost:11434"
    complex_query_threshold: int = 300

class LLMRouter:
    def __init__(self, config: RouterConfig = RouterConfig()):
        self.config = config

    def select_backend(self, query: str) -> Backend:
        if not self._ollama_available():
            print("⚠️  Ollama no disponible → usando nube")
            return Backend.CLOUD
        if len(query) > self.config.complex_query_threshold:
            print("💡 Query compleja → usando nube")
            return Backend.CLOUD
        print("✅ Ollama local activo ($0)")
        return Backend.LOCAL

    def _ollama_available(self) -> bool:
        try:
            r = requests.get(
                f"{self.config.ollama_url}/api/tags",
                timeout=2
            )
            return r.status_code == 200
        except Exception:
            return False
