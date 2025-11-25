import logging
from pathlib import Path
from typing import List

from sec_certs.dataset.fips import FIPSDataset

import config.constants as config
from advanced_parsing.model.advanced_properties import AdvancedProperties
from advanced_parsing.parser import parse_tables
from advanced_parsing.utils import export_adv_prop_to_json
from database.db_manager import (
    insert_file_metadata,
    insert_fips_version,
    setup_db_files,
)
from models.chapter import Chapter
# from pdf_parsing.parser import parse_pdf_to_text
from txt_parsing.chapter_utils import chapters_from_json, chapters_to_json
from txt_parsing.fips_detector import detect_fips_version
from txt_parsing.mapper import extract_chapters_from_text
from txt_parsing.validator import validate_chapters

logger = logging.getLogger(__name__)
logging.getLogger("txt_parsing").setLevel(logging.CRITICAL)


def process_pdfs_to_txt(input_dir: Path, output_dir: Path):
    pdf_files = list(input_dir.rglob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")

    for count, pdf_file in enumerate(pdf_files):
        output_file = output_dir / (pdf_file.stem + ".txt")
        if output_file.exists():
            logger.info(
                f"Skipping {pdf_file.name}, already processed as {output_file.name}"
            )
            continue
        logger.info(f"\nOn {count} / {len(pdf_files)}\nProcessing: {pdf_file}")

        # Parse the PDF
        # parse_pdf_to_text(pdf_file, output_dir)


def map_chapters(input_dir: Path, output_dir: Path, base_chapters_path: Path):
    files = list(input_dir.rglob("*.txt"))
    logger.info(f"Found {len(files)} txt files to process")

    conn = setup_db_files()

    base_chapters = chapters_from_json(base_chapters_path)

    for count, file in enumerate(files):
        if count % 100 == 0:
            logger.info(f"On file {count} of {len(files)}")
        with open(file) as f:
            file_text = f.read()
            chapters: List[Chapter] = extract_chapters_from_text(
                file_text, base_chapters
            )

        error, missing = validate_chapters(chapters)

        # lookup file in the sec_certs library
        dset = FIPSDataset.from_web()
        sec_certs_df = dset.to_pandas()
        try:
            row = sec_certs_df.loc[file.stem]
            insert_file_metadata(file.stem, error, missing, row, conn.cursor())
        except KeyError:
            logger.error(f"File {file.stem} not found in the library")
        if error < config.ERROR_ACCEPT:
            chapters_to_json(chapters, file, output_dir)

    conn.commit()
    conn.close()


def process_fips_versions(input_dir: Path):
    files = list(input_dir.rglob("*.txt"))
    conn = setup_db_files()
    for count, file in enumerate(files):
        with open(file) as f:
            file_text = f.read()

        fips_version = detect_fips_version(file_text)
        insert_fips_version(file.stem, fips_version, conn.cursor())

    conn.commit()
    conn.close()


def process_tables(input_dir: Path, output_dir: Path):
    files = list(input_dir.rglob("*.json"))

    for count, file in enumerate(files):
        logger.info(f"On file {count} of {len(files)}")
        chapters = chapters_from_json(file)
        data: AdvancedProperties = parse_tables(chapters)
        export_adv_prop_to_json(data, file, output_dir)


def main():
    # process_pdfs_to_txt(Path(config.PDF_DIR), Path(config.TXT_DIR))
    map_chapters(
        Path(config.TXT_DIR),
        Path(config.CHAPTERS_JSON_DIR),
        Path(config.BASE_CHAPTERS),
    )
    process_tables(Path(config.CHAPTERS_JSON_DIR), Path(config.TABLES_JSON_DIR))


if __name__ == "__main__":
    main()
