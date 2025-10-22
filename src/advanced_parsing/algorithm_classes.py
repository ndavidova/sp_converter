from dataclasses import dataclass
from typing import List

@dataclass
class AlgoProp:
    name: str
    value: str

"""
From cavpOeAlgo definition
"""
@dataclass
class ApprovedAlgo:
    algorithm: str
    cavpCertName: str
    properties: str
    reference: str


@dataclass
class Algo:
    name: str
    algoPropList: List[AlgoProp]
    implName: str
    reference: str

@dataclass
class NonApprovedAllowedNSC:
    name: str
    caveat: str
    use: str

@dataclass
class NonApprovedNonAllowedAlgo:
    name: str
    use: str