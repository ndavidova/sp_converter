from pathlib import Path
from typing import List, Tuple
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

DOC_CONVERTER = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

def parse_pdf_to_text(pdf_path: Path, output_dir: str | None = None ):
    try:
        result = DOC_CONVERTER.convert(pdf_path)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        text_file = output_path / f"{pdf_path.stem}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(result.document.export_to_text())

        print(f"Text saved to: {text_file}")

    return result.document

def find_pdf_files(input_dir: Path) -> List[Path]:
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return []
    
    return list(input_dir.rglob("*.pdf"))


def process_pdfs(input_dir: Path, output_dir: Path) -> Tuple[int, int]:
    pdf_files = find_pdf_files(input_dir)

    print(f"Found {len(pdf_files)} PDF files to process")
    count = 1
    fail = 0

    for pdf_file in pdf_files:
        output_file = output_dir / (pdf_file.stem + ".txt")
        if output_file.exists():
            print(f"Skipping {pdf_file.name}, already processed as {output_file.name}")
            count += 1
            continue

        # Create corresponding output directory
        print(f"\nOn {count} / {len(pdf_files)}, failed {fail}")
        print(f"\nProcessing: {pdf_file}")
        print(f"Output dir: {output_dir}")

        # Parse the PDF
        if parse_pdf_to_text(pdf_file, output_dir):
            count += 1
        else:
            fail += 1

    return count, fail