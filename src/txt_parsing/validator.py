import logging
from typing import List, Tuple
from txt_parsing.chapter import Chapter

logger = logging.getLogger(__name__)


def validate_chapters(chapters: List[Chapter]) -> Tuple[int, int]:
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