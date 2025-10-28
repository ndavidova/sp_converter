from sec_certs.dataset.fips import FIPSDataset
from pathlib import Path
from typing import List, Tuple
from advanced_parsing.model.advanced_properties import AdvancedProperties
from pdf_parsing.parser import parse_pdf_to_text
from models.chapter import Chapter
from txt_parsing.mapper import extract_chapters_from_text
from txt_parsing.validator import validate_chapters
from database.db_manager import setup_db_files, insert_file_metadata
from txt_parsing.chapter_utils import chapters_to_json, chapters_from_json
from advanced_parsing.parser import parse_tables
from advanced_parsing.utils import export_adv_prop_to_json
import logging

logging.getLogger('txt_parsing').setLevel(logging.CRITICAL)

dset = FIPSDataset.from_web()
sec_certs_df = dset.to_pandas()


def process_pdfs_to_txt(input_dir: Path, output_dir: Path):
    pdf_files = list(input_dir.rglob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for count, pdf_file in enumerate(pdf_files):
        output_file = output_dir / (pdf_file.stem + ".txt")
        if output_file.exists():
            print(f"Skipping {pdf_file.name}, already processed as {output_file.name}")
            count += 1
            continue
        print(f"\nOn {count} / {len(pdf_files)}")
        print(f"\nProcessing: {pdf_file}")

        # Parse the PDF
        if parse_pdf_to_text(pdf_file, output_dir):
            count += 1


def map_chapters(input_dir: Path, output_dir: Path, base_chapters_path: Path):
    files = list(input_dir.rglob("*.txt"))
    print(f"Found {len(files)} txt files to process")

    conn = setup_db_files("file_database.db")

    base_chapters = chapters_from_json(base_chapters_path)

    for count, file in enumerate(files):
        if count % 100 == 0:
            print(f"On file {count} of {len(files)}")
        with open(file) as f:
            chapters: List[Chapter] = extract_chapters_from_text(f.read(), base_chapters)
        
        error, missing = validate_chapters(chapters)
        # lookup file in the sec_certs library
        try:
            row = sec_certs_df.loc[file.stem]
            insert_file_metadata(file.stem, error, missing, row, conn.cursor())
        except KeyError:
            print(f"File {file.stem} not found in the library")
        if error < 10:
            chapters_to_json(chapters, file, output_dir)

    conn.commit()
    conn.close()


def process_tables(input_dir: Path, output_dir: Path):
    files = list(input_dir.rglob("*.json"))

    for count, file in enumerate(files):
        print(f"On file {count} of {len(files)}")
        chapters = chapters_from_json(file)
        data: AdvancedProperties = parse_tables(chapters)
        export_adv_prop_to_json(data, file, output_dir)


def main():
    # pdfs_dir = Path()
    txts_dir = Path("data/input/SP")
    json_chapters_dir = Path("data/output/mapping")
    json_tables_dir = Path("data/output/advanced")
    base_chapters = Path("src/config/base_chapters.json")

    # process_pdfs_to_txt(pdfs_dir, txts_dir)
    # map_chapters(txts_dir, json_chapters_dir, base_chapters)
    process_tables(json_chapters_dir, json_tables_dir)


if __name__ == "__main__":
    main()