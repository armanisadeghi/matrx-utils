import json
import os
import re


def get_supported_extensions(config):
    return tuple(config.get("extensions_for_analysis", [".js", ".jsx", ".ts", ".tsx", ".json", ".mjs"]))


def read_file_content(file_path, config, remove_comments=False):
    if not file_extension_supported(file_path, config):
        return ""

    encodings = ["utf-8", "utf-16", "iso-8859-1"]
    content = ""
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                content = file.read()
            break
        except UnicodeDecodeError:
            pass

    if not content:
        return ""

    file_extension = os.path.splitext(file_path)[-1].lower()
    if remove_comments and file_extension in config.get("remove_comments_for_extensions", []):
        content = remove_comments_from_content(content, file_extension)

    return content


def remove_comments_from_content(content, file_extension):
    if file_extension in [".js", ".jsx", ".ts", ".tsx"]:
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    elif file_extension == ".py":
        content = re.sub(r"#.*", "", content)
        content = re.sub(r"(\'\'\'(.*?)\'\'\'|\"\"\"(.*?)\"\"\")", "", content, flags=re.DOTALL)
    return content


def file_extension_supported(file_path, config):
    supported_exts = get_supported_extensions(config)
    _, extension = os.path.splitext(file_path)
    return extension in supported_exts


def normalize_path(path):
    if not path:
        return path
    norm_path = os.path.normpath(path).replace("\\", "/").lower()
    if os.name == "nt" and ":" in norm_path:
        drive, tail = os.path.splitdrive(norm_path)
        return (drive.upper() + tail).replace("\\", "/")
    return norm_path


def resolve_alias(alias_path, config):
    alias_map = config.get("alias_map", {})
    for alias, base_path in alias_map.items():
        if alias_path.startswith(alias):
            relative_path = alias_path[len(alias):]
            return normalize_path(os.path.join(base_path, relative_path))
    return alias_path


def should_process_file(file_path, config):
    _, extension = os.path.splitext(file_path)
    include_exts = config.get("include_extensions", [])
    ignore_exts = config.get("ignore_extensions", [])
    if include_exts and extension not in include_exts:
        return False
    if extension in ignore_exts:
        return False
    return True


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_structure_to_json(structure, output_file):
    if not output_file:
        return
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=4)
    print(output_file)


def save_combined_structure_to_txt(combined_structure, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        def write_recursive(structure, level=0):
            for key, value in structure.items():
                if key in ["_files", "full_paths"]:
                    continue
                if isinstance(value, dict):
                    f.write("  " * level + f"{key}:\n")
                    write_recursive(value, level + 1)
                else:
                    f.write("  " * level + f"- {key}: {value}\n")
        write_recursive(combined_structure)
    print(output_file)
