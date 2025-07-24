"""
Simple docling PDF parser.
This script parses a PDF file and extracts various elements like text, tables, figures, etc.
"""

import os
import sys
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


def parse_pdf_with_docling(pdf_path: str, output_dir: str | None = None):
    """
    Parse a PDF file using docling and extract various elements.
    
    Args:
        pdf_path (str): Path to the PDF file to parse
        output_dir (str): Optional output directory for results
    """
    print(f"🔍 Parsing PDF: {pdf_path}")
    

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    
    # Set up the document converter
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    try:
        result = doc_converter.convert(pdf_path)
        
        # Print basic document info
        print(f"📊 Document converted successfully!")
        print(f"📄 Title: {result.document.name}")
        print(f"📝 Number of pages: {len(result.document.pages)}")
        
        # Extract and display different types of content
        print("\n🔤 Text Content Preview:")
        print("-" * 50)
        
        # Get document text (first 500 chars)
        doc_text = result.document.export_to_text()
        print(doc_text[:500] + "..." if len(doc_text) > 500 else doc_text)
        
        # Count different element types
        tables = []
        figures = []
        text_blocks = []
        
        for element in result.document.texts:
            if hasattr(element, 'label'):
                if 'table' in element.label.lower():
                    tables.append(element)
                elif 'figure' in element.label.lower():
                    figures.append(element)
                else:
                    text_blocks.append(element)
        
        print(f"\n📈 Content Analysis:")
        print(f"  • Tables found: {len(tables)}")
        print(f"  • Figures found: {len(figures)}")
        print(f"  • Text blocks: {len(text_blocks)}")
        
        # Show table details if any
        if tables:
            print(f"\n📋 Table Details:")
            for i, table in enumerate(tables[:3], 1):  # Show first 3 tables
                print(f"  Table {i}: {getattr(table, 'text', 'N/A')[:100]}...")
        
        # Save outputs if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save as markdown
            markdown_file = output_path / f"{Path(pdf_path).stem}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(result.document.export_to_markdown())
            print(f"\n💾 Markdown saved to: {markdown_file}")
            
            # Save as JSON
            json_file = output_path / f"{Path(pdf_path).stem}.json"
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result.document.model_dump(), f, indent=2, ensure_ascii=False)
            print(f"💾 JSON saved to: {json_file}")
            
            # Save plain text
            text_file = output_path / f"{Path(pdf_path).stem}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(doc_text)
            print(f"💾 Text saved to: {text_file}")
        
        return result.document
        
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        return None


def main():
    """Main function to demonstrate docling PDF parsing."""
    workspace_root = Path(__file__).parent.parent.parent
    pdf_path = workspace_root / "data" / "input" / "pdf" / "79c794728c6beb64.pdf"
    output_dir = workspace_root / "data" / "output" / "docling"
    
    document = parse_pdf_with_docling(str(pdf_path), str(output_dir))


if __name__ == "__main__":
    main()
