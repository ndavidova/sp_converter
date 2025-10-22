from dataclasses import fields
import json
import re
from typing import Dict, List, Tuple, get_args
import regex
import sys
import os
from src.utils.chapter_utils import chapters_from_json, get_chapter
from .model.advanced_properties import AdvancedProperties
from .md_table_iter import parse_markdown_tables


def remove_symbols(name):
    return re.sub(r"[ \-–—‒#,]", "", name)

# def get_table_entry_type(table_instance) -> type:
#     orig_class = getattr(table_instance, '__orig_class__', None)
#     if orig_class is None:
#         return None
#     type_args = get_args(orig_class)
#     return type_args[0] if type_args else object


def parse_tables(file: str) -> AdvancedProperties:
    chapters = chapters_from_json("data/output/mapping/c73e0da9ae79c7cc.json")
    res = AdvancedProperties()
    table = None
    chapter = ""

    for f in fields(res):
        table = getattr(res, f.name)
        if not table.name:
            chapter = get_chapter(chapters, table.section, table.subsection)
        else:
            continue # Case when there are multiple tables in one section   
        entries = parse_markdown_tables(chapter.content)
        constructor = table.entry_type
        for row in entries[1:]:
            element = constructor(*row)
            table.entries.append(element)

            



if __name__ == "__main__":
    # properties = AdvancedProperties("c73e0da9ae79c7cc")
    parse_tables("c73e0da9ae79c7cc.json")
    # print(properties.document_id)

    # properties.json_dump()

