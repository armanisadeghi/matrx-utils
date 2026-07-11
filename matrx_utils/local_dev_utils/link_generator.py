"""
link_generator — Generate Next.js navigation links from a _files-keyed directory structure.
Reads a JSON structure file (from code_context) and produces a links JSON.
"""
import json
import os


def create_links(data, root_directory, base_path="", exclude_dynamic_routes=False):
    links = []
    for key, value in data.items():
        if key in ("_files", "full_paths"):
            continue
        if not isinstance(value, dict):
            continue
        new_base_path = f"{base_path}/{key}" if base_path else f"/{key}"
        if "page.tsx" in value.get("_files", []):
            label = key.replace("-", " ").capitalize()
            link = f"/{root_directory}{new_base_path}"
            if not (exclude_dynamic_routes and ("[" in label or "[" in link)):
                links.append({"label": label, "link": link})
        links.extend(create_links(value, root_directory, new_base_path, exclude_dynamic_routes))
    return links


def process_directory_structure(file_path, root_directory, exclude_dynamic_routes=False):
    with open(file_path, "r") as file:
        data = json.load(file)

    links = create_links(data, root_directory, exclude_dynamic_routes=exclude_dynamic_routes)

    base, ext = os.path.splitext(file_path)
    output_file_path = f"{base}_links{ext}"

    with open(output_file_path, "w") as file:
        json.dump({"links": links}, file, indent=4)

    return links, output_file_path


if __name__ == "__main__":
    file_path = "/path/to/structure.json"
    root_directory = "my-app"
    exclude_dynamic_routes = True

    links, output_file_path = process_directory_structure(file_path, root_directory, exclude_dynamic_routes)
    print(json.dumps({"links": links}, indent=4))
    print(f"Links saved to: {output_file_path}")
