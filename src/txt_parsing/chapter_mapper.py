"""
chapter_mapper.py
-----------------
Extracts and maps chapters and subchapters from text files according to a predefined structure.
"""
import copy
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Iterator, Tuple
import re, regex

logger = logging.getLogger(__name__)


@dataclass
class Chapter:
    title: str
    subchapters: List["Chapter"] = field(default_factory=list)
    optional: bool = False
    content: str = ""
    found: bool = False

"""
Definition of chapters based on the Securicy Policy Template Document version 5.8
(https://csrc.nist.gov/csrc/media/Projects/cryptographic-module-validation-program/documents/fips%20140-3/Module%20Processes/SP%20Template%20-%20V5.8.docx)
"""
GLOBAL_CHAPTERS: List[Chapter] = [
    Chapter(
        "General",
        [
            Chapter("Overview", []),
            Chapter("Security Levels", []),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Cryptographic Module Specification",
        [
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
        ]
    ),
    Chapter(
        "Cryptographic Module Interfaces",
        [
            Chapter("Ports and interfaces", []),
            Chapter("Trusted Channel Specification", [], optional=True),
            Chapter("Control Interface Not Inhibited", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Roles, Services, and Authentication",
        [
            Chapter("Authentication methods", []),
            Chapter("Roles", []),
            Chapter("Approved Services", []),
            Chapter("Non-Approved Services", []),
            Chapter("External Software/Firmware Loaded", []),
            Chapter("Bypass Actions and Status", [], optional=True),
            Chapter("Cryptographic Output Actions and Status", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Software/Firmware Security",
        [
            Chapter("Integrity Techniques", []),
            Chapter("Initiate on Demand", []),
            Chapter("Open-Source Parameters", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Operational Environment",
        [
            Chapter("Operational Environment Type and Requirements", []),
            Chapter("Configuration Settings and Restriction", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Physical Security",
        [
            Chapter("Mechanisms and Actions Required", [], optional=True),
            Chapter("User Placed Tamper Seals", [], optional=True),
            Chapter("Filler Panels", [], optional=True),
            Chapter("Fault Induction Mitigation", [], optional=True),
            Chapter("EFP/EFT Information", [], optional=True),
            Chapter("Hardness Testing Temperature Ranges", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Non-Invasive Security",
        [
            Chapter("Mitigation Techniques", [], optional=True),
            Chapter("Effectiveness", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Sensitive security parameters management",
        [
            Chapter("Storage Areas", []),
            Chapter("SSP Input-Output Methods", []),
            Chapter("SSP Zeroization Methods", []),
            Chapter("SSPs", []),
            Chapter("Transitions", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Self-Tests",
        [
            Chapter("Pre-Operational Self-Tests", []),
            Chapter("Conditional Self-Tests", []),
            Chapter("Periodic Self-Test Information", []),
            Chapter("Error States", []),
            Chapter("Operator Initiation of Self-Tests", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Life-Cycle assurance",
        [
            Chapter("Installation, Initialization, and Startup Procedures", []),
            Chapter("Administrator Guidance", []),
            Chapter("Non-Administrator Guidance", []),
            Chapter("Design and Rules", [], optional=True),
            Chapter("Maintenance Requirements", [], optional=True),
            Chapter("End of Life", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    ),
    Chapter(
        "Mitigation of other attacks",
        [
            Chapter("Attack List", [], optional=True),
            Chapter("Mitigation Effectiveness", [], optional=True),
            Chapter("Guidance and Constraints", [], optional=True),
            Chapter("Additional Information", [], optional=True)
        ]
    )
]

def traverse(chapters: List[Chapter]) -> Iterator[tuple[str, Tuple[int, int]]]:
    """Iterate through all chapters and subchapters with numbering."""
    for i, chapter in enumerate(chapters, 1):
        yield chapter.title, (i, 0)
        for j, sub in enumerate(chapter.subchapters, 1):
            yield sub.title, (i, j)

def substitute(title: str) -> str:
    """Remove spaces and dashes for fuzzy matching."""
    return re.sub(r"[ \-–—‒]", "", title)

def build_chapter_regex(chapter_num: int, subchapter_num: int) -> str:
    """Construct a fuzzy regex for chapter titles."""
    base_chapter = GLOBAL_CHAPTERS[chapter_num - 1]
    title = base_chapter.title
    if subchapter_num > 0:
        title = base_chapter.subchapters[subchapter_num - 1].title

    title = substitute(title)

    return rf"^(##|Section)*{chapter_num}(\.?{subchapter_num})?\.?{title}$"

# Core extraction logic
def extract_chapters_from_text(text: str):
    """
    Extract text between chapter boundaries from the given text.
    """
    chapters = copy.deepcopy(GLOBAL_CHAPTERS)
    curr_chapter, curr_subchapter = 0, 0
    inside_chapter = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        matched = False
        if stripped.startswith("##") or not stripped[0].isalpha():
            for _, (ch_num, sub_num) in traverse(chapters):
                if ch_num < curr_chapter:
                    continue

                ## Match regex with 1 allowed error
                pattern = regex.compile(f"({build_chapter_regex(ch_num, sub_num)}){{e<=1}}", flags=regex.IGNORECASE)
                if pattern.match(substitute(stripped)):
                    inside_chapter, matched = True, True
                    curr_chapter, curr_subchapter = ch_num, sub_num

                    # Needs to be reduced because chapters are numbered from 1
                    target = chapters[curr_chapter - 1]
                    if curr_subchapter:
                        target = target.subchapters[curr_subchapter - 1]
                    target.found = True
                    break

                if matched:
                    break

        if not matched and inside_chapter:
            target = chapters[curr_chapter - 1]
            if curr_subchapter > 0:
                target = target.subchapters[curr_subchapter - 1]
            target.content += "\n" + stripped


    return chapters


# Validation
def check_chapter_content(chapters: List[Chapter]) -> Tuple[int, int]:
    count, error = 0, 0

    for i, chapter in enumerate(chapters, 1):
        if not chapter.found:
            logger.warning("Chapter not found " + str(i) + "!!!")
            error += 1
        for j, sub in enumerate(chapter.subchapters, 1):
            if not sub.content:
                count += 1
                msg =("Subchapter number " + str(i) + "." + str(j) + " has no content.")
                logger.warning(msg if not sub.optional else f"Optional {msg}")
                if not sub.optional:
                    error += 1
    logger.info(f"Total empty subchapters: {count}")
    return error, count

# Export
def export_chapters_to_json(chapters: List[Chapter], file_name: str, output_dir: str = "."):
    """Save chapter structure into formatted JSON."""
    print(f"\nExporting file as json ... {output_dir}/{file_name}.json")
    chapters_dict = [asdict(ch) for ch in chapters]

    with open(output_dir + "/" + file_name + ".json", "w", encoding="utf-8") as f:
        json.dump(chapters_dict, f, indent=4)

# Main execution
def main():
    file_name = "38fc95162021cc1a"
    with open("data/input/SP/fullset" + "/" + file_name + ".txt") as f:
        chapters = extract_chapters_from_text(f.read())
    error, _ = check_chapter_content(chapters)
    if not error:
        export_chapters_to_json(chapters, file_name)



if __name__ == "__main__":
    exit(main())
