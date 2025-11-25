from dataclasses import dataclass

# Tables 14-15


@dataclass
class esvCert:
    vendorName: str
    esvCert: str


# Only present if module is itar
@dataclass
class esvItarCert:
    esvCert: str


@dataclass
class entropySource:
    name: str
    type: str
    opEnv: str
    sampleSize: str
    entropyPerSample: str
    conditionalComp: str
