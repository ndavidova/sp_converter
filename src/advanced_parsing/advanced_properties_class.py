from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple
import json

from algorithm_classes import Algo, ApprovedAlgo, NonApprovedAllowedNSC, NonApprovedNonAllowedAlgo
"""
Definitions for classes are inspired by json https://csrc.nist.gov/csrc/media/Projects/cryptographic-module-validation-program/documents/fips%20140-3/Module%20Processes/SchemaMis-2.8.4.json
and for table description and additional info was followed this document: https://csrc.nist.gov/csrc/media/Projects/cryptographic-module-validation-program/documents/fips%20140-3/Module%20Processes/MIS%20Table%20Descriptions%20-%20V2.8.4.pdf 
"""

# good example is c73e0da9ae79c7cc

@dataclass
class AdvancedProperties:
    document_id: str
    approved_algorithms: List[ApprovedAlgo] = field(default_factory=list)
    vendor_affirmed_algos: List[Algo] = field(default_factory=list)
    non_approved_allowed_algos: List[Algo] = field(default_factory=list)
    non_approved_allowed_NSC: List[NonApprovedAllowedNSC] = field(default_factory=list)
    non_approved_not_allowed: List[NonApprovedNonAllowedAlgo] = field(default_factory=list)

    def json_dump(self):
        with open("data/output/advanced/" + self.document_id + ".json", "w") as f:
            json.dump(asdict(self), f, indent=2) 

    ENTRIES = List[List[str]]
    def construct_properties_from_tables(self, entries: List[ENTRIES]):
        for one in entries[0]:
            alg, cavp, prop, ref = one
            curr = ApprovedAlgo(alg, cavp, prop, ref)
            self.approved_algorithms.append(curr)
        
        for name, caveat, use in entries[3]:
            curr = NonApprovedAllowedNSC(name, caveat, use)
            self.non_approved_allowed_NSC.append(curr)
        
        for name, use in entries[4]:
            curr = NonApprovedNonAllowedAlgo(name, use)
            self.non_approved_not_allowed.append(curr)

