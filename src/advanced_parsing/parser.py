import re
from dataclasses import fields
from typing import List

from fuzzysearch import find_near_matches

import config.constants as config
from models.chapter import Chapter

from .md_tables import filter_table_lines, parse_markdown_tables
from .model.advanced_properties import AdvancedProperties


def get_chapter(chapters: List[Chapter], chapter_num: int, subchapter_num: int):
    return chapters[chapter_num - 1].subchapters[subchapter_num - 1]


def match_sections_between_headers(
    text: str, headers: List[str], max_dev=config.MAX_DEVIATION
) -> List[str]:
    found_matches = []

    for original_header in headers:
        search_term = original_header.strip()

        matches = find_near_matches(
            search_term,
            text,
            max_l_dist=max_dev,
        )

        if matches:
            best_match = matches[0]

            # The content should start from the next \n
            match_end_index = best_match.end
            newline_match = re.search(r"\n", text[best_match.end :])
            if newline_match:
                content_start_index = match_end_index + newline_match.end()
            else:
                content_start_index = match_end_index

            found_matches.append(
                {
                    "start": best_match.start,
                    "content_start": content_start_index,
                    "header_name": original_header.strip(),
                }
            )

    found_matches.sort(key=lambda x: x["start"])

    sections = {}
    matched_headers = []

    for i, current_match in enumerate(found_matches):
        current_header = current_match["header_name"]
        start_index = current_match["content_start"]

        if i + 1 < len(found_matches):
            end_index = found_matches[i + 1]["start"]
        else:
            end_index = len(text)

        content = text[start_index:end_index].strip()

        sections[current_header] = content
        matched_headers.append(current_header)

    return sections, matched_headers


# Section is split into parts by the separator titles
def get_splitted_section(
    text: str, section: int, subsection: int, name: str, adv_prop: AdvancedProperties
) -> str:
    # Get all table names for the given section/subsection
    section_names = [
        getattr(adv_prop, f.name).name
        for f in fields(adv_prop)
        if getattr(adv_prop, f.name).section == section
        and getattr(adv_prop, f.name).subsection == subsection
    ]
    sections, matched = match_sections_between_headers(text, section_names)
    return "" if name not in matched else sections[name]


def parse_tables(chapters: List[Chapter]) -> AdvancedProperties:
    res = AdvancedProperties()
    table = None
    chapter = ""

    for f in fields(res):
        table = getattr(res, f.name)
        chapter = get_chapter(chapters, table.section, table.subsection)
        if table.name == "":
            content = chapter.content
        # Case when there is more tables in one section, the section is split by separators
        if table.name:
            content = get_splitted_section(
                chapter.content, table.section, table.subsection, table.name, res
            )
        tables = parse_markdown_tables(filter_table_lines(content))
        if not tables or len(tables[0]) <= 1:
            continue

        table.found = True

        constructor = table.entry_type
        for row in tables[0][1:]:
            try:
                element = constructor(*row)
                table.entries.append(element)
            except Exception:
                pass

    return res
