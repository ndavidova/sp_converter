import json
import re
from typing import List, Tuple
from markdown_it import MarkdownIt
import regex
from advanced_properties_class import AdvancedProperties

## This could be some de-mapper that maps all chapters back from json, as part of chapter_mapper
## Now it's just for algorithms section to see how it goes
def load_section(file_path = "data/output/fullset/c73e0da9ae79c7cc.json", title = "Algorithms"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            chapters = json.load(file)

        for chapter in chapters:
            if chapter.get("title", "") == "Cryptographic Module Specification":
                subchapters = chapter.get("subchapters", [])
                for sub in subchapters:
                    if sub.get("title") == title:
                        return sub.get("content", "No content available")
        
        return None

    except FileNotFoundError:
        print("Error: File not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")

section_names = ["Approved Algorithms",
                "Vendor-Affirmed Algorithms",
                "Non-Approved, Allowed Algorithms",
                "Non-Approved, Allowed Algorithms with No Security Claimed",
                "Non-Approved, Not Allowed Algorithms"]

def remove_symbols(name):
    return re.sub(r"[ \-–—‒#,]", "", name)

# In this case all section names have to be present, which I don't know if has to be the case
def split_sections(chapter) -> Tuple[List[str], int]:
    sections = ["" for _ in section_names]
    count = 0
    inside = False

    lines = chapter.splitlines()
    for line in lines:
        if not line:
            continue
        
        if re.match(r"^\|", line) and inside:
            sections[count - 1] += line + "\n"

        if count == len(section_names):
            continue

        current = remove_symbols(line.strip())
        expected_name = remove_symbols(section_names[count])
        pattern = re.compile(rf"^{expected_name}\s*:?$", re.IGNORECASE)
        if pattern.match(current):
            count += 1
            inside = True

    return sections, count

def parse_markdown_tables(text):
    md = MarkdownIt("gfm-like")
    tokens = md.parse(text)
    tables = []
    current_table = []
    row = []
    for token in tokens:
        if token.type == "tr_open":
            row = []
        elif token.type in {"th_open", "td_open"}:
            pass
        elif token.type == "inline":
            row.append(token.content.strip())
        elif token.type == "tr_close":
            current_table.append(row)
        elif token.type == "table_close":
            tables.append(current_table)
            current_table = []
    return tables

# For multi-page tables
def merge_tables(tables):
    merged = {}
    for table in tables:
        header = tuple(table[0])
        rows = table[1:]
        if header not in merged:
            merged[header] = []
        merged[header].extend(rows)
    return merged



if __name__ == "__main__":
    # properties: AdvancedProperties = {}
    chapter = load_section()
    # lst, count = split_sections("\n## Approved Algorithms:\n| Algorithm                    | CAVP Cert   | Properties   | Reference         |\n|------------------------------|-------------|--------------|-------------------|\n| AES-CBC                      | A3548       | -            | SP 800-38A        |\n## Vendor-Affirmed Algorithms:\n| Name                     | Properties                                                                                                                                                        | Implementation                            | Reference                                                          |\n")
    lst, count = split_sections(chapter)
    # print(count)
    # print(chapter)
    # print("#############################################")
    # for i in lst:
    #     print("###############################################")
    #     print(i)
    
    # For easier data processing I will merge all the tables (with the same header)
    tables = parse_markdown_tables(lst[0])
    approved = merge_tables(tables)

    nsc = merge_tables(parse_markdown_tables(lst[3]))
    na = merge_tables(parse_markdown_tables(lst[4]))

    properties = AdvancedProperties("c73e0da9ae79c7cc")
    properties.construct_properties_from_tables([list(approved.values())[0], [], [], list(nsc.values())[0], list(na.values())[0]])

    print(properties.document_id)

    properties.json_dump()

