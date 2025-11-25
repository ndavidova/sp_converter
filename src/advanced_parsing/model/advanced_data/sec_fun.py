from dataclasses import dataclass

# In the Table Descriptions document this looks like a nested table, there is [O] column followed by non [O] column


@dataclass
class SecFuncImpl:
    name: str
    type: str
    description: str
    properties: str = ""
    algorithms: str = ""
    algorithm_properties = ""
