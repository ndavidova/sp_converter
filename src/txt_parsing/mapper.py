"""
chapter_mapper.py
-----------------
Extracts and maps chapters and subchapters from text files according to a predefined structure.
"""
import copy
import json
import logging
from typing import List, Tuple
import re, regex

from txt_parsing.chapter import Chapter, chapter_from_dict, chapters_to_json, traverse_chapters, chapters_from_json


logger = logging.getLogger(__name__)

def substitute(title: str) -> str:
    """Remove spaces and dashes for fuzzy matching."""
    return re.sub(r"[ \-–—‒]", "", title)

def build_chapter_regex(chapters: List[Chapter], chapter_num: int, subchapter_num: int) -> str:
    """Construct a fuzzy regex for chapter titles."""
    base_chapter = chapters[chapter_num - 1]
    title = base_chapter.title
    if subchapter_num > 0:
        title = base_chapter.subchapters[subchapter_num - 1].title

    title = substitute(title)

    return rf"^(##|Section)*{chapter_num}(\.?{subchapter_num})?\.?{title}$"

# Core extraction logic
def extract_chapters_from_text(text: str, base_chapters = List[Chapter]):
    """
    Extract text between chapter boundaries from the given text.
    """
    chapters = copy.deepcopy(base_chapters)
    curr_chapter, curr_subchapter = 0, 0
    inside_chapter = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        matched = False
        if stripped.startswith("##") or not stripped[0].isalpha():
            for _, (ch_num, sub_num) in traverse_chapters(chapters):
                if ch_num < curr_chapter:
                    continue

                ## Match regex with 1 allowed error
                pattern = regex.compile(f"({build_chapter_regex(chapters, ch_num, sub_num)}){{e<=1}}", flags=regex.IGNORECASE)
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

# Main execution
def main():
    with open("src/txt_parsing/base_chapters.json") as f:
        base_chapters = chapters_from_json(f.read())
    
    file_name = "38fc95162021cc1a"
    with open("data/input/SP/fullset" + "/" + file_name + ".txt") as f:
        chapters = extract_chapters_from_text(f.read(), base_chapters)
    error, _ = check_chapter_content(chapters)
    if not error:
        chapters_to_json(chapters, file_name)



if __name__ == "__main__":
    exit(main())
