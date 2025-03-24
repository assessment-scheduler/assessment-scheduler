from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Solver(ABC):
    @abstractmethod
    def solve(self) -> Optional[List[tuple]]:
        pass

