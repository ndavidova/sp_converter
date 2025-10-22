from dataclasses import dataclass

# Tables 20, 21

class Role:
    name: str
    # Can be one of: “Role” “Identify” “Multi-Factor Identity”, but now for simplicity will be just str
    type: str
    operatorType: str
    authMethodList: str