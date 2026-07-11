"""
create_directories — Scaffold a directory/file structure from a dict definition.
Useful for bootstrapping new Next.js features or module layouts.
"""
import os

# Example structure — edit this dict to match your desired scaffold
structure = {
    "components": [
        "ComposeEmail.tsx",
        "EmailItem.tsx",
        "EmailList.tsx",
        "EmailView.tsx",
    ],
    "hooks": [
        "useEmails.ts",
    ],
    "redux": [
        "store.ts",
        "emailsSlice.ts",
        "providers.tsx",
    ],
    "supabase": [
        "client.ts",
    ],
    "types": [
        "email.ts",
    ],
    "app/inbox": [
        "page.tsx",
        "layout.tsx",
    ],
    "app/compose": [
        "page.tsx",
        "layout.tsx",
    ],
    "app/emails/[id]": [
        "page.tsx",
    ],
}


def create_structure(base_dir, structure):
    for folder, files in structure.items():
        folder_path = os.path.join(base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write("")


def create_additional_files(base_dir):
    additional_files = [
        "app/layout.tsx",
        "app/globals.css",
    ]
    for file in additional_files:
        file_path = os.path.join(base_dir, file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")


def main(base_directory=None):
    if not base_directory:
        base_directory = input(
            "Enter the directory in which you want to create the structure "
            "(leave blank for current directory): "
        ).strip() or os.getcwd()

    create_structure(base_directory, structure)
    create_additional_files(base_directory)

    print(f"Directories and files created in {base_directory}.")


if __name__ == "__main__":
    base_directory = "/path/to/new/feature"
    main(base_directory)
