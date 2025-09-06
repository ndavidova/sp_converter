"""
Simple chapter mapper that finds text between main chapter boundaries.
"""
import json
from dataclasses import dataclass, field, asdict
from typing import List, Iterator, Tuple
import re, regex

from schema_loader import SchemaLoader
FILENAME = "38fc95162021cc1a"

@dataclass
class Chapter:
    title: str
    subchapters: list["Chapter"] = field(default_factory=list)
    optional: bool = False
    content: str = ""
    found: bool = False

chapters: List[Chapter] = [
    Chapter("General", [
        Chapter("Overview", []),
        Chapter("Security Levels", []),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Cryptographic Module Specification", [
        Chapter("Description", []),
        Chapter("Tested and vendor affirmed module version and identification", []),
        Chapter("Excluded components", []),
        Chapter("Modes of operation", []),
        Chapter("Algorithms", []),
        Chapter("Security Function Implementations", []),
        Chapter("Algorithm Specific Information", []),
        Chapter("RBG and Entropy", []),
        Chapter("Key Generation", []),
        Chapter("Key Establishment", []),
        Chapter("Industry protocols", []),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Cryptographic Module Interfaces", [
        Chapter("Ports and interfaces", []),
        Chapter("Trusted Channel Specification", [], optional=True),
        Chapter("Control Interface Not Inhibited", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Roles, Services, and Authentication", [
        Chapter("Authentication methods", []),
        Chapter("Roles", []),
        Chapter("Approved Services", []),
        Chapter("Non-Approved Services", []),
        Chapter("External Software/Firmware Loaded", []),
        Chapter("Bypass Actions and Status", [], optional=True),
        Chapter("Cryptographic Output Actions and Status", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Software/Firmware Security", [
        Chapter("Integrity Techniques", []),
        Chapter("Initiate on Demand", []),
        Chapter("Open-Source Parameters", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Operational Environment", [
        Chapter("Operational Environment Type and Requirements", []), 
        Chapter("Configuration Settings and Restriction", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Physical Security", [
        Chapter("Mechanisms and Actions Required", [], optional=True),
        Chapter("User Placed Tamper Seals", [], optional=True),
        Chapter("Filler Panels", [], optional=True),
        Chapter("Fault Induction Mitigation", [], optional=True),
        Chapter("EFP/EFT Information", [], optional=True),
        Chapter("Hardness Testing Temperature Ranges", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Non-Invasive Security", [
        Chapter("Mitigation Techniques", [], optional=True), 
        Chapter("Effectiveness", [], optional=True), 
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Sensitive security parameters management", [
        Chapter("Storage Areas", []),
        Chapter("SSP Input-Output Methods", []),
        Chapter("SSP Zeroization Methods", []),
        Chapter("SSPs", []),
        Chapter("Transitions", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Self-Tests", [
        Chapter("Pre-Operational Self-Tests", []),
        Chapter("Conditional Self-Tests", []),
        Chapter("Periodic Self-Test Information", []),
        Chapter("Error States", []),
        Chapter("Operator Initiation of Self-Tests", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ]),
    Chapter("Life-Cycle assurance", [
        Chapter("Installation, Initialization, and Startup Procedures", []),
        Chapter("Administrator Guidance", []),
        Chapter("Non-Administrator Guidance", []),
        Chapter("Design and Rules", [], optional=True),
        Chapter("Maintenance Requirements", [], optional=True),
        Chapter("End of Life", [], optional=True),
        Chapter("Additional Information", [], optional=True)

    ]),
    Chapter("Mitigation of other attacks", [
        Chapter("Attack List", [], optional=True),
        Chapter("Mitigation Effectiveness", [], optional=True),
        Chapter("Guidance and Constraints", [], optional=True),
        Chapter("Additional Information", [], optional=True)
    ])
]

def traverse(lst) -> Iterator[tuple[str, Tuple[int, int]]]:
    for i, chapter in enumerate(lst, 1):
        yield chapter.title, (i, 0)
        for j, sub in enumerate(chapter.subchapters, 1):
            yield sub.title, (i, j)

def chapter_regex(chapter_num, subchapter_num):
    number_pattern = str(chapter_num)
    chapter = chapters[chapter_num - 1].title
    if subchapter_num > 0:
        number_pattern += r"\." + str(subchapter_num)
        chapter = chapters[chapter_num - 1].subchapters[subchapter_num - 1].title

    chapter = re.sub(r"[ \-–—‒]", "", chapter)

    full_pattern = rf"^(##|Section)*{number_pattern}\.?{chapter}$"
    return full_pattern

def extract_chapters_from_text(text: str):
    """
    Extract text between main chapter boundaries.

    Args:
        text: Full text content

    """
    # Counting from 1 so when accessing the chapters, it needs to be lowered by 1 to access the appropriate object
    current_chapter_num: int = 0
    current_subchapter_num: int = 0
    inside_chapter = False

    lines = text.split('\n')

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        chapter_found = False
        # traverse through all chapter texts
        if stripped_line.startswith("##") or not stripped_line[0].isalpha():
            for _, (num, sub_num) in traverse(chapters):
                if num < current_chapter_num:
                    continue
                sub_lower = re.sub(r"[ \-–—‒]", "",stripped_line)
                ## Match regex with 1 allowed error
                pattern = regex.compile(f"({chapter_regex(num, sub_num)}){{e<=1}}", flags=regex.IGNORECASE)
                if pattern.match(sub_lower):
                    inside_chapter = True
                    current_chapter_num = num
                    current_subchapter_num = sub_num
                    if current_subchapter_num > 0:
                        chapters[current_chapter_num - 1].subchapters[current_subchapter_num - 1].found = True
                    else:
                        chapters[current_chapter_num - 1].found = True
                    chapter_found = True
                    break
                if chapter_found:
                    break

        if not chapter_found and inside_chapter:
            if current_subchapter_num > 0:
                chapters[current_chapter_num - 1].subchapters[current_subchapter_num - 1].content += "\n" + stripped_line
            else:
                chapters[current_chapter_num - 1].content += "\n" + stripped_line



def check_chapter_content():
    count = 0
    error = 0
    for i, chapter in enumerate(chapters, 1):
        if not chapter.found:
            print("⚠️ Chapter not found " + str(i) + "!!!")
            error += 1
        for j, sub in enumerate(chapter.subchapters, 1):
            if not sub.content:
                count += 1
                if not sub.optional:
                    print("⚠️ Warning, non-optional subchapter number " + str(i) + "." + str(j) + " has no content.")
                    error += 1
                else:
                    print("Optional subchapter " + str(i) + "." + str(j) + " has no content.")
            if not sub.found and not sub.optional:
                print("⚠️ Non-optional subchapter not found " +  str(i) + "." + str(j) + "!")
                error += 1
    print("Total subchapters: " + str(count) + " are empty")
    return error, count


def export_chapters_to_json():
    print(f"\nExporting file as json ... {FILENAME}.json")
    chapters_dict = [asdict(ch) for ch in chapters]

    with open("data/output/json/" + FILENAME + ".json", "w", encoding="utf-8") as f:
        json.dump(chapters_dict, f, indent=4)

def main():
    with open("data/output/base/SP/" + FILENAME + ".txt") as f:
        extract_chapters_from_text(f.read())
    error, _ = check_chapter_content()
    if not error:
        export_chapters_to_json()



if __name__ == "__main__":
    exit(main())
