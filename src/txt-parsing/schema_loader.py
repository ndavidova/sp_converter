"""
Schema loader module for handling JSONC (JSON with comments) files.
Provides functionality to load, clean, and validate JSON schema files.
"""

import json
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from typing import Dict, Any, Optional, List
import jsonschema


class SchemaLoader:
    """Handles loading and validation of JSON schema files with comments."""
    
    def __init__(self, schema_path: str):
        """Initialize the schema loader with a path to the schema file."""
        self.schema_path = Path(schema_path)
        self.raw_content: Optional[str] = None
        self.cleaned_content: Optional[str] = None
        self.schema: Optional[Dict[str, Any]] = None
        
    def load_raw_content(self) -> str:
        """Load the raw content from the schema file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
            return self.raw_content
        except Exception as e:
            raise IOError(f"Error reading schema file: {e}")
    
    def remove_comments(self, content: Optional[str] = None) -> str:
        """Remove comments from JSONC content."""
        if content is None:
            if self.raw_content is None:
                self.load_raw_content()
            content = self.raw_content
        
        if content is None:
            raise ValueError("No content available to process")
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line_num, line in enumerate(lines):
            # Skip comment removal for first 3 lines (schema metadata)
            if line_num < 3:
                cleaned_lines.append(line)
            else:
                # Remove // comments from line 4 onwards
                if '//' in line:
                    line = line[:line.index('//')].rstrip()
                cleaned_lines.append(line)
        
        self.cleaned_content = '\n'.join(cleaned_lines)
        return self.cleaned_content
    
    def parse_json(self, content: Optional[str] = None) -> Dict[str, Any]:
        """Parse the cleaned JSON content."""
        if content is None:
            if self.cleaned_content is None:
                self.remove_comments()
            content = self.cleaned_content
        
        if content is None:
            raise ValueError("No content available to parse")
        
        try:
            self.schema = json.loads(content)
            if self.schema is None:
                raise ValueError("Parsed schema is None")
            return self.schema
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON syntax: {e}")
    
    def validate_schema(self, schema: Optional[Dict[str, Any]] = None) -> bool:
        """Validate that the loaded content is a valid JSON schema."""
        if schema is None:
            if self.schema is None:
                self.parse_json()
            schema = self.schema
        
        if schema is None:
            raise ValueError("No schema available to validate")
        
        try:
            # Validate against JSON Schema meta-schema
            jsonschema.Draft202012Validator.check_schema(schema)
            return True
        except jsonschema.SchemaError as e:
            raise ValueError(f"Invalid JSON schema: {e}")
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Get the properties section of the schema."""
        if self.schema is None:
            self.load_and_validate()
        
        if self.schema is None:
            raise ValueError("Schema is None after loading")
        
        return self.schema.get('properties', {})
    
    def get_required_fields(self, section_name: Optional[str] = None) -> List[str]:
        """Get required fields for a section or the entire schema."""
        if self.schema is None:
            self.load_and_validate()
        
        if self.schema is None:
            raise ValueError("Schema is None after loading")
        
        if section_name is None:
            return self.schema.get('required', [])
        
        properties = self.get_schema_properties()
        if section_name in properties:
            section_schema = properties[section_name]
            return section_schema.get('required', [])
        
        return []
    
    def get_section_properties(self, section_name: str) -> Dict[str, Any]:
        """Get properties for a specific section."""
        properties = self.get_schema_properties()
        if section_name not in properties:
            raise ValueError(f"Section '{section_name}' not found in schema")
        
        section_schema = properties[section_name]
        return section_schema.get('properties', {})
    
    def load_and_validate(self) -> Dict[str, Any]:
        """Load, clean, parse, and validate the schema in one step."""
        self.load_raw_content()
        self.remove_comments()
        self.parse_json()
        self.validate_schema()
        if self.schema is None:
            raise ValueError("Schema is None after loading and validation")
        return self.schema
    
    def save_cleaned_schema(self, output_path: str) -> None:
        """Save the cleaned schema to a file."""
        if self.schema is None:
            self.load_and_validate()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.schema, f, indent=2, ensure_ascii=False)
    
    def print_schema_info(self) -> None:
        """Print information about the loaded schema."""
        if self.schema is None:
            self.load_and_validate()
        
        if self.schema is None:
            raise ValueError("Schema is None after loading")
        
        print(f"Schema loaded from: {self.schema_path}")
        print(f"Schema ID: {self.schema.get('$id', 'N/A')}")
        print(f"Title: {self.schema.get('title', 'N/A')}")
        print(f"Description: {self.schema.get('description', 'N/A')}")
        
        properties = self.get_schema_properties()
        print(f"Number of top-level properties: {len(properties)}")
        print("\nTop-level sections:")
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get('type', 'unknown')
            required = prop_name in self.get_required_fields()
            required_str = " (required)" if required else " (optional)"
            print(f"  - {prop_name}: {prop_type}{required_str}")
    
    def __repr__(self) -> str:
        """String representation of the schema loader."""
        return f"SchemaLoader(path='{self.schema_path}', loaded={self.schema is not None})"


def load_schema(schema_path: str) -> Dict[str, Any]:
    """Convenience function to load and validate a schema file."""
    loader = SchemaLoader(schema_path)
    return loader.load_and_validate()


def main():
    """Command line interface for the schema loader."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load and validate JSON schema files")
    parser.add_argument("schema_file", help="Path to the JSON schema file")
    parser.add_argument("--info", action="store_true", help="Print schema information")
    parser.add_argument("--clean", help="Save cleaned schema to file")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't load")
    
    args = parser.parse_args()
    
    try:
        loader = SchemaLoader(args.schema_file)
        
        if args.validate_only:
            loader.load_and_validate()
            print("✓ Schema is valid")
        else:
            schema = loader.load_and_validate()
            print("✓ Schema loaded and validated successfully")
            
            if args.info:
                print("\n" + "="*50)
                loader.print_schema_info()
            
            if args.clean:
                loader.save_cleaned_schema(args.clean)
                print(f"✓ Cleaned schema saved to: {args.clean}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 