from typing import List, Optional, Dict, Union
from policy_executor import PolicyExecutor
from common import vcprint


def apply_batch_policies(
    table_names: List[str],
    database_project: str,
    policy_types: Optional[List[str]] = None,
) -> Dict[str, Union[bool, Dict[str, bool]]]:
    """
    Apply specified RLS policies to multiple tables in batch.
    ONLY generates and applies new policies - never deletes existing ones.

    Args:
        table_names: List of names of tables to apply policies to
        database_project: Database project identifier
        policy_types: List of policy types to apply ('view', 'insert', 'update', 'delete')
                     If None, applies all policy types

    Returns:
        Dictionary with status of each policy application per table
    """
    # Initialize the executor
    executor = PolicyExecutor(database_project=database_project)

    # Apply the access function first (only need to do this once)
    vcprint(f"Applying auth_has_access function to {database_project}...", color="green")
    access_result = executor.apply_access_function()

    if not access_result:
        vcprint("Failed to apply auth_has_access function. Aborting.", color="red")
        return {"auth_has_access_function": False}

    vcprint("Successfully applied auth_has_access function!", color="green")

    results = {"auth_has_access_function": access_result}

    # Apply policies to each table INDEPENDENTLY
    for table_name in table_names:
        vcprint(f"Processing table: {table_name}", color="green")

        if policy_types is None or set(policy_types) >= {
            "view",
            "insert",
            "update",
            "delete",
        }:
            # Apply all policy types
            vcprint(f"Applying all policy types to {table_name}", color="green")
            table_results = executor.apply_all_policies(table_name)
        else:
            # Apply specific policy types
            vcprint(
                f"Applying only these policy types to {table_name}: {', '.join(policy_types)}",
                color="green",
            )

            table_results = {}
            if "view" in policy_types:
                table_results["view"] = executor.apply_view_policy(table_name)
            if "insert" in policy_types:
                table_results["insert"] = executor.apply_insert_policy(table_name)
            if "update" in policy_types:
                table_results["update"] = executor.apply_update_policy(table_name)
            if "delete" in policy_types:
                table_results["delete"] = executor.apply_delete_policy(table_name)

        results[table_name] = table_results
        vcprint(f"Finished processing table: {table_name}", color="green")

    # Calculate overall success status
    successful_tables = sum(
        1
        for table, result in results.items()
        if table != "auth_has_access_function" and ((isinstance(result, bool) and result) or (isinstance(result, dict) and all(result.values())))
    )

    vcprint(
        f"Successfully applied policies to {successful_tables} of {len(table_names)} tables",
        color="green",
    )

    return results


if __name__ == "__main__":
    # Simple variable declarations for batch processing
    table_names = ["recipe", "conversation", "message", "applet"]
    database_project = "supabase_automation_matrix"
    policy_types = None  # None for all policies, or list like ['view', 'update']

    # Call the function with these arguments
    results = apply_batch_policies(
        table_names=table_names,  # ONLY these tables will be modified
        database_project=database_project,
        policy_types=policy_types,
    )

    # Print results summary
    vcprint(
        data=results,
        title="Batch Policy Results",
        pretty=True,
        verbose=True,
        color="blue",
    )
