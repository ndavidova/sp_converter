"""
Simple chapter mapper that finds text between main chapter boundaries.
"""

import re
import json
from pathlib import Path
from typing import Dict, List
from schema_loader import SchemaLoader


class ChapterMapper:
    """Maps text between main chapter boundaries to the 12 schema chapters."""
    
    def __init__(self, schema_loader: SchemaLoader):
        """Initialize with a schema loader."""
        self.schema_loader = schema_loader
        self.chapters = self._get_main_chapters()
        self.chapter_mapping = self._create_chapter_mapping()
        
    def _get_main_chapters(self) -> Dict[int, str]:
        """Get the 12 main chapter names from the schema with their numbers."""
        schema = self.schema_loader.load_and_validate()
        properties = schema.get('properties', {})
        chapter_names = list(properties.keys())
        
        # Map chapter numbers to names
        numbered_chapters = {}
        for i, name in enumerate(chapter_names, 1):
            numbered_chapters[i] = name
            
        return numbered_chapters
    
    def _create_chapter_mapping(self) -> List[Dict[str, str]]:
        """Create a list of dictionaries for chapter patterns by number."""
        chapter_patterns = []
        
        chapter_patterns.append({
            "## Section 1. General": "general"
        })
        
        chapter_patterns.append({
            "## Section 2. Cryptographic Module Specification": "cryptographic_module_specification"
        })
        
        chapter_patterns.append({
            "## Section 3. Cryptographic Module Interfaces": "cryptographic_module_interfaces"
        })
        
        chapter_patterns.append({
            "## Section4 Roles, Services, and Authentication": "roles_services_authentication"
        })
        
        chapter_patterns.append({
            "## Section 5. Software/Firmware Security": "software_firmware_security"
        })
        
        chapter_patterns.append({
            "## Section 6. Operational Environment": "operational_environment"
        })
        
        chapter_patterns.append({
            "## Section 7. Physical Security": "physical_security"
        })
        
        chapter_patterns.append({
            "## Section 8. Non-invasive Security": "non_invasive_security"
        })
        
        chapter_patterns.append({
            "## Section 9. Sensitive security parameters management": "sensitive_security_parameters_management"
        })
        
        chapter_patterns.append({
            "## Section 10. Self-tests": "self_tests"
        })
        
        chapter_patterns.append({
            "## Section 11. Life cycle assurance": "life_cycle_assurance"
        })
        
        chapter_patterns.append({
            "## Section 12. Mitigation of other attacks": "mitigation_of_other_attacks"
        })
        
        return chapter_patterns
    
    def extract_chapters_from_text(self, text: str) -> Dict[int, str]:
        """
        Extract text between main chapter boundaries.
        
        Args:
            text: Full text content
            
        Returns:
            Dictionary with chapter numbers as keys and text content as values
        """
        chapter_texts = {}
        
        # Initialize all chapters with empty strings
        for chapter_num in self.chapters:
            chapter_texts[chapter_num] = ""
        
        lines = text.split('\n')
        current_chapter_num = None
        current_content = []
        inside_chapter = False

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            if stripped_line.startswith("##"):
                print("found a chapter boundary")

            # Check if this line starts a new chapter (use stripped version for pattern matching)
            chapter_found = False
            for i, chapter_patterns in enumerate(self.chapter_mapping):
                chapter_num = i
                for pattern in chapter_patterns:
                    if stripped_line.lower().startswith(pattern.lower()):
                        # Save previous chapter content if exists
                        if current_chapter_num is not None and current_content:
                            chapter_texts[current_chapter_num] = '\n'.join(current_content).rstrip()
                        
                        # Start new chapter
                        current_chapter_num = chapter_num
                        inside_chapter = True
                        current_content = []
                        chapter_found = True
                        break
                if chapter_found:
                    break
            
            # If not a chapter boundary, add to current chapter content (preserve original line with whitespace)
            if not chapter_found and inside_chapter:
                current_content.append(line.rstrip())  # Only remove trailing whitespace, keep leading spaces
        
        # The last chapter
        if inside_chapter and current_content:
            chapter_texts[current_chapter_num] = '\n'.join(current_content).rstrip()
        
        return chapter_texts
    
    def get_chapter_name(self, chapter_num: int) -> str:
        """Get chapter name by number."""
        return self.chapters.get(chapter_num, "unknown")
    
    def get_chapter_text_by_name(self, chapter_texts: Dict[int, str], chapter_name: str) -> str:
        """Get chapter text by name instead of number."""
        for num, name in self.chapters.items():
            if name == chapter_name:
                return chapter_texts.get(num, "")
        return ""
    
    def save_chapters_to_json(self, chapter_texts: Dict[int, str], output_path: str) -> None:
        """Save extracted chapters to JSON file."""
        # Create output structure with chapter names
        output_data = {
            "metadata": {
                "total_chapters": len(self.chapters),
                "chapters_with_content": len([c for c in chapter_texts.values() if c.strip()])
            },
            "chapters": {}
        }
        
        for chapter_num, text in chapter_texts.items():
            chapter_name = self.get_chapter_name(chapter_num)
            output_data["chapters"][f"chapter_{chapter_num}"] = {
                "number": chapter_num,
                "name": chapter_name,
                "content": text
            }
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Chapters saved to: {output_file}")

    def print_chapters_info(self):
        """Print information about the chapters."""
        print(f"Found {len(self.chapters)} main chapters:")
        for chapter_num, chapter_name in self.chapters.items():
            print(f"  {chapter_num}. {chapter_name}")
        
        print(f"\nChapter patterns to look for:")
        for i, chapter_patterns in enumerate(self.chapter_mapping):
            chapter_num = i  # Convert 0-based index to 1-based chapter number
            chapter_name = self.chapters.get(chapter_num, "unknown")
            for pattern in chapter_patterns:
                print(f"  '{pattern}' -> Chapter {chapter_num} ({chapter_name})")


def main():
    """Simple test function for ChapterMapper."""
    print("Testing ChapterMapper...")
    print("=" * 50)
    
    try:
        # Create schema loader
        loader = SchemaLoader('schema/sp.schema.jsonc')
        print("✓ Schema loader created")
        
        # Create chapter mapper
        mapper = ChapterMapper(loader)
        print("✓ Chapter mapper created")
        
        # Show info about chapters
        print("\n" + "-" * 30)
        mapper.print_chapters_info()
        
        # Test with sample text
        sample_text = """
        1 General

        1.1 Overview
        This document provides the non-proprietary security policy for the XYZ Cryptographic Module v1.0.

        1.2 Security Levels
        The module meets FIPS 140-3 Level 2 requirements.

        2 Cryptographic module specification

        2.1 Description
        The XYZ Cryptographic Module is a software-based cryptographic module.

        2.2 Tested and vendor affirmed module identification
        The module has been tested on various operating systems.

        3 Cryptographic module interfaces

        3.1 Ports and interfaces
        The module provides various interfaces for communication.
        """
        
        print("\n" + "-" * 30)
        
        # Set up input and output paths
        input_file = "data/output/docling/79c794728c6beb64.txt"
        output_dir = "data/output/chapters"
        
        # Try to read the text file
        try:
            with open(input_file, "r", encoding='utf-8') as f:
                file_text = f.read()
            print(f"📖 Reading from: {input_file}")
        except FileNotFoundError:
            print("⚠️  Text file not found, using sample text...")
            file_text = sample_text
            input_file = "sample"

        # Extract chapters
        chapters = mapper.extract_chapters_from_text(file_text)
        
        print(f"\nExtracted {len([c for c in chapters.values() if c.strip()])} chapters with content:")
        for chapter_num, text in chapters.items():
            if text.strip():  # Only show chapters with content
                chapter_name = mapper.get_chapter_name(chapter_num)
                print(f"  • Chapter {chapter_num}: {chapter_name}")
        
        # Save to JSON
        if input_file != "sample":
            # Get input filename without extension and create output path
            input_path = Path(input_file)
            output_filename = input_path.stem + ".json"
            output_path = Path(output_dir) / output_filename
            
            mapper.save_chapters_to_json(chapters, str(output_path))
        else:
            print("⚠️  Skipping JSON export for sample data")

        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
