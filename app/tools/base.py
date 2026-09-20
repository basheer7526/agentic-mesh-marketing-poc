from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    Base interface for tools available to agents.
    """

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool and return a structured result.
        """
        raise NotImplementedError