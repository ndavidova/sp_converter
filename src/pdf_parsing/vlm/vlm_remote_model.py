from pathlib import Path
import logging
import os
from pathlib import Path
from typing import Optional
import requests
from docling_core.types.doc.page import SegmentedPage
from dotenv import load_dotenv
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
import requests
from docling_core.types.doc.page import SegmentedPage
from dotenv import load_dotenv
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

def lms_vlm_options(model: str, prompt: str, format: ResponseFormat):
    options = ApiVlmOptions(
        url="http://localhost:1234/v1/chat/completions",  # the default LM Studio
        params=dict(
            model=model,
        ),
        prompt=prompt,
        timeout=90,
        scale=1.0,
        response_format=format,
    )
    return options

def parse_pdf_with_docling(pdf_path: str, output_dir: str | None = None ):
    """
    Parse PDF with docling, optionally using tesseract OCR.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for results
        use_tesseract: Whether to use tesseract OCR (requires tesseract installed)
    """


    pipeline_options = VlmPipelineOptions(
        enable_remote_services=True
    )

    pipeline_options.vlm_options = lms_vlm_options(
        model="smoldocling-256m-preview-mlx-docling-snap",
        prompt="Convert this page to docling.",
        format=ResponseFormat.DOCTAGS,
    )


    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=pipeline_options
            ),
        }
    )

    try:
        result = converter.convert(pdf_path)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None

    
    doc_text = result.document.export_to_text()

    if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            
            markdown_file = output_path / f"{Path(pdf_path).stem}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(result.document.export_to_markdown())
            print(f"\n💾 Markdown saved to: {markdown_file}")
            
            json_file = output_path / f"{Path(pdf_path).stem}.json"
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result.document.model_dump(), f, indent=2, ensure_ascii=False)
            print(f"💾 JSON saved to: {json_file}")
            
            text_file = output_path / f"{Path(pdf_path).stem}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(doc_text)
            print(f"💾 Text saved to: {text_file}")

    return result.document



def process_pdfs_recursively(input_dir: str = "data/input", output_base_dir: str = "data/output/docling/vlm2"):
    """
    Recursively process all PDF files in input_dir, preserving directory structure in output.
    
    Args:
        input_dir: Root input directory to search for PDFs
        output_base_dir: Base output directory 
    """
    
    input_path = Path(input_dir)
    output_base_path = Path(output_base_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory does not exist: {input_dir}")
        return
    
    # Find all PDF files recursively
    pdf_files = list(input_path.rglob("*.pdf"))
    
    if not pdf_files:
        print(f"📄 No PDF files found in {input_dir}")
        return
    
    print(f"🔍 Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        try:
            # Calculate relative path from input_dir to preserve structure
            relative_path = pdf_file.relative_to(input_path)
            
            # Create corresponding output directory
            output_dir = output_base_path / relative_path.parent
            
            print(f"\n📄 Processing: {pdf_file}")
            print(f"📁 Output dir: {output_dir}")
            
            # Parse the PDF
            result = parse_pdf_with_docling(
                pdf_path=str(pdf_file),
                output_dir=str(output_dir), 
            )
            
            if result:
                print(f"✅ Successfully processed: {pdf_file.name}")
            else:
                print(f"❌ Failed to process: {pdf_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {e}")


def main():
    """
    Main function to process all PDFs in data/input directory recursively.
    Preserves directory structure in output.
    """
    
    print("🚀 Starting recursive PDF processing with docling...")
    print("=" * 60)
    
    # Process all PDFs with standard OCR
    print("\n📋 Processing with standard OCR...")
    process_pdfs_recursively()
    


if __name__ == "__main__":
    main()