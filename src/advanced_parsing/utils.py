import json
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

from .model.advanced_properties import AdvancedProperties
from .model.table import Table


def table_asdict(table: Table):
    """Exports the Table to a dictionary with required keys."""
    entries_list = [asdict(entry) for entry in table.entries]
    return {
        "section": table.section,
        "subsection": table.subsection,
        "found": table.found,
        "entries": entries_list,
    }


def adv_asdict(adv: AdvancedProperties):
    res = {}
    for f in fields(adv):
        table = getattr(adv, f.name)
        res[f.name] = table_asdict(table)
    return res


def export_adv_prop_to_json(
    data: AdvancedProperties, file: Path, output_dir: Path, indent: int = 4
):
    output_path = output_dir / f"{file.stem}.json"
    print(f"Exporting file to {output_path}")
    if not is_dataclass(data):
        raise TypeError("Expected a dataclass instance (e.g., AdvancedProperties)")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(adv_asdict(data), f, indent=indent)
