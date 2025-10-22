from dataclasses import dataclass, field
from typing import Generic, List, Tuple, Type, TypeVar
from .table_entry import TableEntry


T = TypeVar("T", bound="TableEntry")
@dataclass
class Table(Generic [T]):
    name: str
    section: int
    subsection: int
    entry_type: Type[T]
    found: bool = False
    entries: List[T] = field(default_factory=list)
    # header: List[str]
    # optional: List[bool]
