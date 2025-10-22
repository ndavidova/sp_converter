from dataclasses import dataclass, field
from typing import Generic, List, Tuple, TypeVar
from model.table_entry import TableEntry


T = TypeVar("T", bound="TableEntry")
@dataclass
class Table(Generic [T]):
    section: Tuple[int, int]
    name: SystemError
    found: bool = False
    entries: List[T] = field(default_factory=list)
    # header: List[str]
    # optional: List[bool]