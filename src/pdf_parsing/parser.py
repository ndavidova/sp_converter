import logging
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

logger = logging.getLogger(__name__)


pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

DOC_CONVERTER = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)


def parse_pdf_to_text(pdf_path: Path, output_dir: str | None = None):
    try:
        result = DOC_CONVERTER.convert(pdf_path)
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return None

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        text_file = output_path / f"{pdf_path.stem}.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(result.document.export_to_text())

        print(f"Text saved to: {text_file}")

    return result.document
