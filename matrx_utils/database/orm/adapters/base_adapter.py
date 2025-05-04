# matrx_utils\database\orm\adapters\base_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Tuple
from types import TracebackType
from typing import Type, Optional


class BaseAdapter(ABC):
    @abstractmethod
    async def execute_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def fetch(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def fetch_by_id(self, model: Any, record_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def count(self, query: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def exists(self, query: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def insert(self, query: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def bulk_insert(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def bulk_update(self, query: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def delete(self, query: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def raw_sql(self, sql: str, params: List[Any] = None) -> Union[List[Dict[str, Any]], int]:
        pass

    @abstractmethod
    async def transaction(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        await self.close()
