
from dataclasses import dataclass
from model.table_entry import TableEntry

# Tables 8-12
# AlgoProp is actually a Key:Value pair, but for simplicity it is represented as a string

@dataclass
class ApprovedAlgo(TableEntry):
    algorithm: str
    cavpCertName: str
    properties: str
    reference: str

# Used for tables 6,7
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