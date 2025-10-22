from dataclasses import dataclass

# Table 13 is a nested table, will be skipped for now

@dataclass
class SecFuncImpl:
    name: str
    type: str
    description: str
    properties: str
