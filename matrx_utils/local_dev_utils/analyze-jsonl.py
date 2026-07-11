#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

def get_schema(data):
    """
    Recursively extract the structural schema of a JSON object.
    Returns a hashable tuple representation.
    """
    if isinstance(data, dict):
        # Sort keys to ensure consistent schema hashing regardless of key order
        return ("dict", tuple(sorted((k, get_schema(v)) for k, v in data.items())))
    elif isinstance(data, list):
        if not data:
            return ("list", tuple())
        # Get unique schemas of all items in the list
        item_schemas = sorted(list(set(get_schema(item) for item in data)), key=lambda x: str(x))
        return ("list", tuple(item_schemas))
    elif isinstance(data, str):
        return ("type", "string")
    elif isinstance(data, bool):
        return ("type", "boolean")
    elif isinstance(data, int):
        return ("type", "integer")
    elif isinstance(data, float):
        return ("type", "float")
    elif data is None:
        return ("type", "null")
    else:
        return ("type", type(data).__name__)

def schema_to_json_friendly(schema):
    """
    Convert the hashable schema tuple back into a standard dictionary/list
    structure for clean JSON serialization.
    """
    tag = schema[0]
    if tag == "dict":
        return {k: schema_to_json_friendly(v) for k, v in schema[1]}
    elif tag == "list":
        return [schema_to_json_friendly(item) for item in schema[1]]
    elif tag == "type":
        return schema[1]
    return "unknown"

def analyze_jsonl(filepath):
    filepath = Path(filepath)
    if not filepath.exists() or not filepath.is_file():
        raise FileNotFoundError(f"File '{filepath}' does not exist.")
        
    schemas_count = defaultdict(int)
    total_lines = 0
    error_lines = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                schema = get_schema(data)
                schemas_count[schema] += 1
                total_lines += 1
            except json.JSONDecodeError:
                error_lines += 1
                
    # Sort schemas by frequency descending
    sorted_schemas = sorted(schemas_count.items(), key=lambda x: x[1], reverse=True)
                
    return {
        "filepath": filepath,
        "total_lines": total_lines,
        "error_lines": error_lines,
        "sorted_schemas": sorted_schemas
    }

def print_and_save_report(results):
    filepath = results["filepath"]
    total_lines = results["total_lines"]
    error_lines = results["error_lines"]
    sorted_schemas = results["sorted_schemas"]

    print(f"Analyzing {filepath.name}...")
    
    if total_lines == 0:
        print("No valid JSON lines found in the file.")
        if error_lines > 0:
            print(f"Encountered {error_lines} invalid JSON lines.")
        return

    # Try importing rich for nice terminal output
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax
        from rich.text import Text
        console = Console()
        has_rich = True
    except ImportError:
        has_rich = False

    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append(f"JSONL Schema Analysis Report: {filepath.name}")
    report_lines.append(f"Total valid JSON lines analyzed: {total_lines}")
    if error_lines > 0:
        report_lines.append(f"Invalid JSON lines skipped: {error_lines}")
    report_lines.append(f"Total unique schemas found: {len(sorted_schemas)}")
    report_lines.append("=" * 60)
    report_lines.append("")

    if has_rich:
        console.print(Panel(
            f"Analyzed [bold cyan]{total_lines}[/] lines\nFound [bold green]{len(sorted_schemas)}[/] unique structures\nSkipped [bold red]{error_lines}[/] invalid lines",
            title="Analysis Summary",
            expand=False
        ))
    else:
        for line in report_lines[:7]: # Print header block if no rich
            print(line)

    for i, (schema, count) in enumerate(sorted_schemas, 1):
        percentage = (count / total_lines) * 100 if total_lines > 0 else 0
        
        friendly_schema = schema_to_json_friendly(schema)
        schema_str = json.dumps(friendly_schema, indent=2)
        
        # Build text report lines
        report_lines.append(f"--- Schema #{i} ---")
        report_lines.append(f"Count: {count} ({percentage:.1f}% of total)")
        report_lines.append("Structure:")
        report_lines.append(schema_str)
        report_lines.append("\n")
        
        # Terminal output
        if has_rich:
            header = Text(f"Schema #{i} - Count: {count} ({percentage:.1f}%)", style="bold yellow")
            console.print(header)
            console.print(Syntax(schema_str, "json", theme="monokai", background_color="default"))
            console.print()
        else:
            print(f"--- Schema #{i} ---")
            print(f"Count: {count} ({percentage:.1f}% of total)")
            print("Structure:")
            print(schema_str)
            print()

    # Determine where to save the text report
    script_dir = Path(__file__).resolve().parent
    pkg_dir = script_dir.parent.parent # e.g. matrx-utils/matrx_utils/local_dev_utils -> matrx-utils
    
    tmp_dir = pkg_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    # Write report
    output_file = tmp_dir / f"{filepath.stem}_schema_analysis.txt"
    output_file.write_text("\n".join(report_lines), encoding='utf-8')
    
    msg = f"✅ Analysis saved to: file://{output_file.absolute()}"
    if has_rich:
        console.print(Panel(msg, style="bold green", expand=False))
    else:
        print("=" * 60)
        print(msg)
        print("=" * 60)

if __name__ == "__main__":
    file_path = "/Users/armanisadeghi/code/junk/convo-exampe.jsonl"

    results = analyze_jsonl(file_path)
    print_and_save_report(results)

