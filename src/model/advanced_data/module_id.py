from dataclasses import dataclass

# Tables 2,3,4,5,6
@dataclass
class TestedHw:
    modelPartNum: str
    hwVersion: str
    processors: str
    features: str # optional

class TestedSwFwHy:
    packageFileName: str
    swFwVersion: str
    features: str # optional
    integrityTest: str

class TestedHyHw:
    modelPartNum: str
    hwVersion: str
    fwVersion: str # optional
    processors: str # optional
    features: str # optional

class TestedOpEnvSwFwHy:
    operatingSystem: str
    hardwarePlatform: str
    processors: str
    paa_pai: str
    hypervisorHostOs: str # optional
    version: str

class OpEnvSwFwHyVA:
    operatingSystem: str
    hardwarePlatform: str