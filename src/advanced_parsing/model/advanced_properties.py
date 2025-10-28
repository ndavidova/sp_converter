from dataclasses import dataclass, field
from .table import Table
from .advanced_data.algorithms import *
from .advanced_data.auth import *
from .advanced_data.entropy import *
from .advanced_data.err_states import *
from .advanced_data.key import *
from .advanced_data.modes_of_op import *
from .advanced_data.module_id import *
from .advanced_data.physical_sec import *
from .advanced_data.ports import *
from .advanced_data.sec_fun import *
from .advanced_data.sec_levels import *
from .advanced_data.self_tests import *
from .advanced_data.services import *
from .advanced_data.ssp import *

@dataclass
class AdvancedProperties:    
    # Security Levels
    security_levels: Table[SecurityLevel] = field(
        default_factory=lambda: Table("", 1, 2, SecurityLevel)
    )

    # Tested Module Identification
    tested_module_id_hw: Table[TestedHw] = field(
        default_factory=lambda: Table("Tested Module Identification - Hardware", 2, 2, TestedHw)
    )
    tested_module_id_sw_fw_hy: Table[TestedSwFwHy] = field(
        default_factory=lambda: Table("Tested Module Identification – Software, Firmware, Hybrid", 2, 2, TestedSwFwHy)
    )
    tested_module_id_hw_hy: Table[TestedHyHw] = field(
        default_factory=lambda: Table("Tested Module Identification – Hybrid Disjoint Hardware", 2, 2, TestedHyHw)
    )
    tested_op_env_sw_fw_hy: Table[TestedOpEnvSwFwHy] = field(
        default_factory=lambda: Table("Tested Operational Environments - Software, Firmware, Hybrid", 2, 2, TestedOpEnvSwFwHy)
    )
    vendor_affirmed_op_env_sw_fw_hy: Table[OpEnvSwFwHyVA] = field(
        default_factory=lambda: Table("Vendor-Affirmed Operational Environments - Software, Firmware, Hybrid", 2, 2, OpEnvSwFwHyVA)
    )

    # Modes of Operation
    modes_of_operation: Table[ModeOfOp] = field(
        default_factory=lambda: Table("", 2, 4, ModeOfOp)
    )

    # Algorithms
    approved_algorithms: Table[ApprovedAlgo] = field(
        default_factory=lambda: Table("Approved Algorithms", 2, 5, ApprovedAlgo)
    )
    vendor_affirmed_algos: Table[Algo] = field(
        default_factory=lambda: Table("Vendor-Affirmed Algorithms", 2, 5, Algo)
    )
    non_approved_allowed_algos: Table[Algo] = field(
        default_factory=lambda: Table("Non-Approved, Allowed Algorithms", 2, 5, Algo) 
    ) 
    non_approved_allowed_NSC: Table[NonApprovedAllowedNSC] = field(
        default_factory=lambda: Table("Non-Approved, Allowed Algorithms with No Security Claimed", 2, 5, NonApprovedAllowedNSC)
    )
    non_approved_not_allowed: Table[NonApprovedNonAllowedAlgo] = field(
        default_factory=lambda: Table("Non-Approved, Not Allowed Algorithms", 2, 5, NonApprovedNonAllowedAlgo)
    )

    # Ports and Interfaces
    ports_interfaces: Table[PortInterface] = field(
        default_factory=lambda: Table("", 3, 1, PortInterface)
    )

    # Authentication Methods
    authentication_methods: Table[AuthMethod] = field(
        default_factory=lambda: Table("", 4, 1, AuthMethod)
    )
    roles: Table[Role] = field(
        default_factory=lambda: Table("", 4, 2, Role)
    )

    # Services
    approved_services: Table[ApprovedService] = field(
        default_factory=lambda: Table("", 4, 3, ApprovedService)
    )
    non_approved_services: Table[NonApprovedService] = field(
        default_factory=lambda: Table("", 4, 4, NonApprovedService)
    )

    # Physical Security
    mechanisms_actions: Table[PhSecMechanism] = field(
        default_factory=lambda: Table("", 7, 1, PhSecMechanism)
    )

    # SSPs
    storage_areas: Table[StorageArea] = field(
        default_factory=lambda: Table("", 9, 1, StorageArea)
    )

    ssp_io_methods : Table[SspIOMethod] = field(
        default_factory=lambda: Table("", 9, 2, SspIOMethod)
    )

    ssp_zeroization_methods : Table[SspZeroization] = field(
        default_factory=lambda: Table("", 9, 3, SspZeroization)
    )
    # Self Tests
    self_tests: Table[SelfTest] = field(
        default_factory=lambda: Table("", 10, 1, SelfTest)
    )
    cond_self_tests: Table[CondSelfTest] = field(
        default_factory=lambda: Table("", 10, 2, CondSelfTest)
    )

    # Error States
    error_states: Table[ErrorState] = field(
        default_factory=lambda: Table("", 10, 4, ErrorState)
    )
