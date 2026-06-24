from abc import ABC, abstractmethod
from typing import Optional
from .orbit_models import OrbitQueryPayload, OrbitResponse

class OrbitClient(ABC):
    @abstractmethod
    def query(self, payload: OrbitQueryPayload) -> OrbitResponse:
        pass

    @abstractmethod
    def get_mode_info(self) -> str:
        pass
