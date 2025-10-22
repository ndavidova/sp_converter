#!/usr/bin/env python3
"""
Simple Docling + Ollama Pipeline for Hierarchy Detection

Usage:
    python docling_ollama_pipeline.py input.pdf
    python docling_ollama_pipeline.py input.pdf --output-dir results/
"""

import json
import requests
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


def parse_pdf_with_docling(pdf_path: str) -> str:
    """Extract text from PDF using regular docling."""
    
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # Skip OCR to avoid PyTorch loading issues
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    result = converter.convert(pdf_path)
    
    return result.document.export_to_text()


def analyze_hierarchy_with_ollama(text: str, model: str = "qwen3:8b") -> dict:
    """Send text to local Ollama for hierarchy analysis."""
    
    prompt = f"""
Extract numbered sections and nest them correctly. Return JSON only.

NESTING RULES:
- Section "1.1" goes INSIDE section "1" (in its subsections array)
- Section "1.2" goes INSIDE section "1" (in its subsections array)  
- Section "2.1" goes INSIDE section "2" (in its subsections array)
- Section "2.2" goes INSIDE section "2" (in its subsections array)
etc.

NEVER put "1.1" or "1.2" as top-level sections!

JSON format:
{{
    "sections": [
        {{
            "number": "1",
            "title": "General",
            "content": "content for section 1",
            "subsections": [
                {{
                    "number": "1.1",
                    "title": "Overview", 
                    "content": "content for section 1.1",
                    "subsections": []
                }},
                {{
                    "number": "1.2",
                    "title": "Security",
                    "content": "content for section 1.2", 
                    "subsections": []
                }}
            ]
        }},
        {{
            "number": "2",
            "title": "Specification",
            "content": "content for section 2",
            "subsections": [
                {{
                    "number": "2.1",
                    "title": "Description",
                    "content": "content for section 2.1",
                    "subsections": []
                }}
            ]
        }}
    ]
}}
If there is no content in top level section, keep content field empty.

Document:
{text}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
    )
    
    # Debug: Print the response to see what we got
    print(f"API Response Status: {response.status_code}")
    response_data = response.json()
    print(f"Response keys: {list(response_data.keys())}")
    
    if "response" not in response_data:
        print(f"Full response: {response_data}")
        raise Exception(f"Unexpected response structure: {response_data}")
    
    try:
        return json.loads(response_data["response"])
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        print(f"Response length: {len(response_data['response'])} characters")
        
        # Save the raw response for debugging
        try:
            with open("debug_raw_response.json", 'w', encoding='utf-8') as f:
                f.write(response_data["response"])
            print("Raw response saved to debug_raw_response.json for inspection")
        except Exception as save_error:
            print(f"Could not save raw response: {save_error}")
        
        # Try to fix common JSON issues
        try:
            # Try to add missing closing brackets/braces if truncated
            raw_response = response_data["response"].strip()
            if raw_response.endswith(','):
                raw_response = raw_response[:-1]  # Remove trailing comma
            
            # Try to fix incomplete JSON by adding missing closing brackets
            open_braces = raw_response.count('{') - raw_response.count('}')
            open_brackets = raw_response.count('[') - raw_response.count(']')
            
            fixed_response = raw_response
            for _ in range(open_brackets):
                fixed_response += ']'
            for _ in range(open_braces):
                fixed_response += '}'
                
            print(f"Attempting to fix JSON: added {open_brackets} ']' and {open_braces} '}}'")
            return json.loads(fixed_response)
            
        except json.JSONDecodeError as fix_error:
            print(f"JSON fix attempt failed: {fix_error}")
            print(f"First 500 characters: {response_data['response'][:500]}")
            print(f"Last 500 characters: {response_data['response'][-500:]}")
            # Return a simple fallback structure with nested format
            return {"sections": []}


def save_results(hierarchy: dict, pdf_path: str, output_dir: str, input_text: str = None):
    """Save hierarchy results and optionally the input text fed to the model."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save the input text that was fed to the model
    if input_text:
        input_file = output_path / f"{Path(pdf_path).stem}_input.txt"
        try:
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(f"# Input text fed to model for: {Path(pdf_path).stem}\n\n")
                f.write(input_text)
            print(f"Input text saved: {input_file}")
        except Exception as e:
            print(f"Error saving input text: {e}")
    else:
        print("No input text provided to save")
    
    # Save structured JSON
    json_file = output_path / f"{Path(pdf_path).stem}_hierarchy.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    
    # Save readable markdown with nested structure
    md_file = output_path / f"{Path(pdf_path).stem}_hierarchy.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# {Path(pdf_path).stem}\n\n")
        
        def write_section(section, header_level=2):
            """Recursively write sections and subsections to markdown."""
            # Debug: Check what type we got
            if not isinstance(section, dict):
                print(f"WARNING: Expected dict, got {type(section)}: {section}")
                return
                
            # Write section header
            number = section.get('number', 'Unknown')
            title = section.get('title', 'Untitled')
            f.write(f"{'#' * header_level} {number} {title}\n\n")
            
            # Write section content
            content = section.get('content', '').strip()
            if content:
                f.write(f"{content}\n\n")
            
            # Write subsections recursively
            subsections = section.get('subsections', [])
            if isinstance(subsections, list):
                for subsection in subsections:
                    write_section(subsection, header_level + 1)
            else:
                print(f"WARNING: Expected list for subsections, got {type(subsections)}: {subsections}")
        
        # Process all top-level sections
        for section in hierarchy.get("sections", []):
            write_section(section)
    
    print(f"Results saved: {json_file} and {md_file}")
    if input_text:
        print(f"Input text also saved: {output_path / f'{Path(pdf_path).stem}_input.txt'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--output-dir", "-o", default="output", help="Output directory")
    parser.add_argument("--model", default="qwen3:8b", help="Ollama model to use")
    
    args = parser.parse_args()
    
    print(f"📄 Extracting text from: {args.pdf_path}")
    text = parse_pdf_with_docling(args.pdf_path)
    
    print(f"🤖 Analyzing hierarchy with: {args.model}")
    hierarchy = analyze_hierarchy_with_ollama(text, args.model)
    
    print(f"💾 Saving results to: {args.output_dir}")
    save_results(hierarchy, args.pdf_path, args.output_dir, text)
    
    print("✅ Done!")


if __name__ == "__main__":
    main()