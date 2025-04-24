import os
import sys
from git import Repo, GitCommandError, InvalidGitRepositoryError
from matrx_utils import vcprint

# ====== IMPORTANT: If save_direct = True in generator.py, live files will be overwritten with auto-generated files ======

# If this environmental variable is set to your actual project root, auto-generated python files will overwrite the live, existing files
ADMIN_PYTHON_ROOT = os.getenv("ADMIN_PYTHON_ROOT", "")

# If this environmental variable is set to your actual project root, auto-generated typescript files will overwrite the live, existing files
ADMIN_TS_ROOT = os.getenv("ADMIN_TS_ROOT", "")


def check_git_status(save_direct):
    """
    Check if ADMIN_PYTHON_ROOT and ADMIN_TS_ROOT are git repositories
    and verify if there are any uncommitted changes.
    Returns True if it's safe to proceed (no changes), False otherwise.
    """
    roots_to_check = [
        ("Admin Python Root", ADMIN_PYTHON_ROOT),
        ("Admin TypeScript Root", ADMIN_TS_ROOT),
    ]
    has_issues = False

    if not save_direct:
        vcprint(
            "[MATRX GIT CHECKER] save_direct is False - skipping git checks",
            color="green",
        )
        return True

    vcprint("\n[MATRX GIT CHECKER] Checking git repository status...", color="yellow")
    vcprint(f"[MATRX GIT CHECKER] ADMIN_PYTHON_ROOT: {ADMIN_PYTHON_ROOT}", color="green")
    vcprint(f"[MATRX GIT CHECKER] ADMIN_TS_ROOT: {ADMIN_TS_ROOT}", color="green")
    print()

    for root_name, root_path in roots_to_check:
        vcprint(f"\n[MATRX GIT CHECKER] Checking {root_name}...", color="yellow")

        # Skip if path is not set
        if not root_path:
            vcprint(f"- {root_name} path not set", color="yellow")
            continue

        # Check if path exists
        if not os.path.exists(root_path):
            vcprint(f"- {root_name} path '{root_path}' does not exist", color="red")
            continue

        try:
            # Try to initialize repo object
            repo = Repo(root_path)
            vcprint("- Git repository found! ✓", color="green")
            vcprint("- Checking git status...\n", color="green")

            # Check if there are uncommitted changes
            if repo.is_dirty(untracked_files=True):
                vcprint("- Uncommitted changes detected! Details:\n", color="red")

                # Show modified files
                modified = repo.git.status("--porcelain").split("\n")
                if any(line.strip() for line in modified):
                    vcprint("  Modified files:", color="red")
                    for line in modified:
                        if line.strip():
                            vcprint(f"    {line.strip()}", color="red")

                has_issues = True
            else:
                vcprint("- No uncommitted changes found ✓", color="green")

        except InvalidGitRepositoryError:
            vcprint("- Not a git repository ✓", color="green")
            vcprint("- Proceeding as regular directory...", color="green")
            continue
        except GitCommandError as e:
            vcprint(f"- Error checking git status: {str(e)}", color="red")
            has_issues = True
        except Exception as e:
            vcprint(f"- Unexpected error: {str(e)}", color="red")
            has_issues = True

    if has_issues:
        vcprint(
            "\n[MATRX GIT CHECKER] Error: Cannot proceed with save_direct=True\n",
            color="red",
        )
        vcprint(
            "[MATRX GIT CHECKER] Your Options:\n --> Option 1: Commit or stash your changes first.\n --> Option 2: Set save_direct=False.\n --> Option 3: Change your environmental variables to point to a different or temporary directory.\n",
            color="red",
        )
        sys.exit(1)
    else:
        vcprint("\n[MATRX GIT CHECKER] All checks passed ✓", color="green")

    return True


def clear_terminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    clear_terminal()

    schema = "public"
    database_project = "supabase_automation_matrix"
    additional_schemas = ["auth"]
    save_direct = False

    if save_direct:
        check_git_status(save_direct)
        input("WARNING: This will overwrite the existing schema files. Press Enter to continue...")
