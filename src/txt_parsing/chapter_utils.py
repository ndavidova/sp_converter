from dataclasses import asdict
import json
from pathlib import Path
from typing import Iterator, List, Tuple
from models.chapter import Chapter


def traverse_chapters(chapters: List[Chapter]) -> Iterator[tuple[str, Tuple[int, int]]]:
    """Iterate through all chapters and subchapters with numbering."""
    for i, chapter in enumerate(chapters, 1):
        yield chapter.title, (i, 0)
        for j, sub in enumerate(chapter.subchapters, 1):
            yield sub.title, (i, j)


def chapters_to_json(chapters: List[Chapter], file: Path, output_dir: Path, indent: int = 4) -> None:
    """Save chapter structure into formatted JSON."""
    filename = file.stem
    print(f"\nExporting file as json ... {output_dir}/{filename}.json")
    with open(output_dir / (filename + ".json"), "w", encoding="utf-8") as f:
        json.dump([asdict(ch) for ch in chapters], f, indent=indent)


def chapter_from_dict(data: dict) -> Chapter:
    """Recursively reconstruct a Chapter (and subchapters) from a dict."""
    return Chapter(
        title = data["title"],
        subchapters = [chapter_from_dict(sc) for sc in data.get("subchapters", [])],
        optional = data.get("optional", False),
        content = data.get("content", ""),
        found = data.get("found", False),
    )


def chapters_from_json(file_path: Path) -> List[Chapter]:
    """Load a list of Chapter objects from a JSON string."""
    with open(file_path, 'r', encoding='utf-8') as f:
        json_str = f.read()
    data = json.loads(json_str)
    return [chapter_from_dict(ch) for ch in data]

