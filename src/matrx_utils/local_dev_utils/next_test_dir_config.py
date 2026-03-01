"""
next_test_dir_config — Generate a TypeScript config file listing Next.js page routes.

Scans a Next.js app directory for directories containing page.tsx and generates
a typed TypeScript config file (config.ts) with the ModulePage structure.
"""
import os
import re
import time

from matrx_utils.code_context import CodeContextBuilder


def extract_pages(data, path=""):
    """
    Recursively extract directories containing page.tsx from a _files-keyed structure.
    Returns a list of relative path strings.
    """
    pages = []
    for key, value in data.items():
        if key in ("_files", "full_paths"):
            continue
        if not isinstance(value, dict):
            continue
        new_path = f"{path}/{key}" if path else key
        if "page.tsx" in value.get("_files", []):
            pages.append(new_path)
        pages.extend(extract_pages(value, new_path))
    return pages


def format_title(directory_name):
    return " ".join(word.capitalize() for word in directory_name.split("-"))


def generate_typescript_code(pages):
    ts_code = """// config.ts

import {ModulePage} from "@/components/matrx/navigation/types";

export const pages: ModulePage[] = [
"""
    for page in pages:
        title = format_title(page.split("/")[-1])
        ts_code += f"""    {{
        title: '{title}',
        path: '{page}',
        relative: true,
        description: ''
    }},
"""
    ts_code += """];

export const filteredPages = pages.filter(page => page.path !== 'link-here');

export const MODULE_HOME = '/some-module';
export const MODULE_NAME = 'Module Name';
"""
    return ts_code


def save_typescript_code(code, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as file:
        file.write(code)
    print(f"TypeScript code saved to {output_file}")


def main(config):
    root_dir = config["root_directory"]
    save_path = config.get("root_save_path", os.path.join(os.getcwd(), "temp", "dir_structure"))

    builder = CodeContextBuilder(
        project_root=root_dir,
        output_mode="tree_only",
        overrides={
            "include_files": {"add": ["page.tsx"]},
        },
        show_all_tree_directories=False,
        prune_empty_directories=True,
    )
    result = builder.build()
    structure = result.to_files_json(root=builder.project_root)

    pages_with_page_tsx = extract_pages(structure)
    typescript_code = generate_typescript_code(pages_with_page_tsx)

    unique_suffix = time.strftime("%y%m%S")
    sanitized_root = re.sub(r'[\\/:*?"<>|()]', "-", root_dir)
    output_file = os.path.join(save_path, f"dir_{sanitized_root}_{unique_suffix}.ts")

    save_typescript_code(typescript_code, output_file)


if __name__ == "__main__":
    config = {
        "root_directory": "/path/to/your/next/app",
        "root_save_path": os.path.join(os.getcwd(), "temp", "dir_structure"),
    }
    main(config)
