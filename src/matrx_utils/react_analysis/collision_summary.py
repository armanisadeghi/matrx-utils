import os

from matrx_utils.react_analysis.name_collision_analyer import find_name_collisions, analyze_file_collisions
from matrx_utils.react_analysis.utils import load_json, save_structure_to_json


def summarize_collisions(name_collisions):
    summary = {
        "total_collisions": len(name_collisions),
        "most_frequent_collisions": sorted(
            name_collisions.items(), key=lambda item: len(item[1]), reverse=True
        )[:10],
    }
    summary["most_frequent_collisions"] = [
        {"name": name, "occurrences": len(paths), "files": paths}
        for name, paths in summary["most_frequent_collisions"]
    ]
    return summary


def summarize_file_collisions(page_collisions):
    file_summaries = {
        file: {
            "total_exports": len(data["exports"]),
            "total_imports": len(data["imports"]),
            "total_collisions": len(data["exports"]) + len(data["imports"]),
        }
        for file, data in page_collisions.items()
    }

    return {
        "total_files_with_collisions": len(page_collisions),
        "files_with_most_collisions": sorted(
            file_summaries.items(),
            key=lambda item: item[1]["total_collisions"],
            reverse=True,
        )[:10],
    }


def get_full_collision_summary(combined_structure, config, verbose=True):
    name_collisions = find_name_collisions(combined_structure)
    page_collisions = analyze_file_collisions(combined_structure, name_collisions)

    collision_summary = summarize_collisions(name_collisions)
    file_collision_summary = summarize_file_collisions(page_collisions)

    if verbose:
        import json
        print("\nCollision Summary:")
        print(json.dumps(collision_summary, indent=2))
        print("\nFile Collision Summary:")
        print(json.dumps(file_collision_summary, indent=2))

    top_files = file_collision_summary["files_with_most_collisions"]
    top_10_offenders = {
        "top_name_collisions": {
            c["name"]: c["occurrences"] for c in collision_summary["most_frequent_collisions"]
        },
        "top_file_collisions": {
            fd[0]: fd[1]["total_collisions"] for fd in top_files
        },
    }

    full_summary = {
        "name_collisions": collision_summary,
        "file_collisions": file_collision_summary,
        "top_10_offenders": top_10_offenders,
    }

    save_structure_to_json(collision_summary, config.get("output_collision_summary_file"))
    save_structure_to_json(file_collision_summary, config.get("output_file_collision_summary_file"))
    save_structure_to_json(full_summary, config.get("output_full_collision_summary_file"))

    return full_summary
