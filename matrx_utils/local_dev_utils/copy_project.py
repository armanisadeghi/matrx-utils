"""
copy_project — Copy a project directory to a new location with progress reporting.
Excludes common build artifacts, lockfiles, and IDE directories by default.
"""
import os
import shutil


def count_items(source_dir, exclude_dirs, exclude_files):
    total_items = 0
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        total_items += len(dirs)
        total_items += len([f for f in files if f not in exclude_files])
    return total_items


def copy_directory_with_progress(
    source_dir,
    destination_dir,
    exclude_dirs=None,
    exclude_files=None,
):
    """
    Copy source_dir to destination_dir, skipping excluded dirs/files and printing progress.

    Args:
        source_dir:       Source directory path.
        destination_dir:  Destination directory path.
        exclude_dirs:     List of directory names to skip. Uses common defaults if None.
        exclude_files:    List of filenames to skip. Uses common defaults if None.
    """
    default_exclude_dirs = [
        "node_modules",
        ".git",
        "venv",
        ".venv",
        ".next",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "build",
        ".idea",
        ".vscode",
    ]

    default_exclude_files = [
        ".gitignore",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Pipfile.lock",
        ".env",
        ".DS_Store",
        "Thumbs.db",
    ]

    exclude_dirs = exclude_dirs or default_exclude_dirs
    exclude_files = exclude_files or default_exclude_files

    print(f"Copying '{source_dir}' → '{destination_dir}'")
    print(f"Excluding dirs:  {exclude_dirs}")
    print(f"Excluding files: {exclude_files}")

    total_items = count_items(source_dir, exclude_dirs, exclude_files)
    print(f"Total items to copy: {total_items}\n")

    items_copied = 0

    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        dest_path = os.path.join(destination_dir, relative_path)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
            items_copied += 1

        for file in files:
            if file not in exclude_files:
                shutil.copy(os.path.join(root, file), os.path.join(dest_path, file))
                items_copied += 1

            if total_items:
                progress = (items_copied / total_items) * 100
                print(f"\rProgress: {progress:.1f}% ({items_copied}/{total_items})", end="")

    print("\nCopy completed.")


if __name__ == "__main__":
    source_dir = "/path/to/source/project"
    destination_dir = "/path/to/destination/copy"
    copy_directory_with_progress(source_dir, destination_dir)
