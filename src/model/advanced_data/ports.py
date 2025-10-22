from dataclasses import dataclass

# Table 19
@dataclass
class PortInterface:
    physicalPort: str
    # Multiselect from “Data Input” “Data Output” “Control Input” “Control Output” “Status Output” “Power” “None”
    # Could be changed to enum in the future
    logicalInterface: str
    data: str