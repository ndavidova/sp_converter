
from dataclasses import dataclass
from ..table_entry import TableEntry

# Tables 5,6,7,8,9
# AlgoProp is actually a Key:Value pair, but for simplicity it is represented as a string

@dataclass
class ApprovedAlgo(TableEntry):
    algorithm: str
    cavpCertName: str
    properties: str
    reference: str

# Used for tables
@dataclass
class Algo(TableEntry):
    name: str
    algoPropList: str
    implName: str
    reference: str

@dataclass
class NonApprovedAllowedNSC(TableEntry):
    name: str
    caveat: str
    use: str

@dataclass
class NonApprovedNonAllowedAlgo(TableEntry):
    name: str
    use: str