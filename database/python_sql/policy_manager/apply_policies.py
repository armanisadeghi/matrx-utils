from typing import List, Optional, Dict, Union
from policy_generator import PolicyExecutor
from common import vcprint

def apply_policies(
    table_name: str,
    database_project: str,
    policy_types: Optional[List[str]] = None
) -> Dict[str, Union[bool, Dict[str, bool]]]:
    """
    Apply specified RLS policies to a table.
    ONLY generates and applies new policies - never deletes existing ones.

    Args:
        table_name: Name of the table to apply policies to
        database_project: Database project identifier
        policy_types: List of policy types to apply ('view', 'insert', 'update', 'delete')
                     If None, applies all policy types
    
    Returns:
        Dictionary with status of each policy application
    """
    # Initialize the executor
    executor = PolicyExecutor(database_project=database_project)
    
    # Apply the access function first
    vcprint(f"Applying auth_has_access function to {database_project}...", color='green')
    access_result = executor.apply_access_function()
    
    if not access_result:
        vcprint("Failed to apply auth_has_access function. Aborting.", color='red')
        return {"auth_has_access_function": False}
    
    vcprint("Successfully applied auth_has_access function!", color='green')
    
    # Apply the policies to THIS SPECIFIC TABLE ONLY
    vcprint(f"Applying policies to table: {table_name}", color='green')
    
    results = {"auth_has_access_function": access_result}
    
    if policy_types is None or set(policy_types) >= {'view', 'insert', 'update', 'delete'}:
        # Apply all policy types
        vcprint(f"Applying all policy types to {table_name}", color='green')
        table_results = executor.apply_all_policies(table_name)
    else:
        # Apply specific policy types
        vcprint(f"Applying only these policy types to {table_name}: {', '.join(policy_types)}", color='green')
        
        table_results = {}
        if 'view' in policy_types:
            table_results['view'] = executor.apply_view_policy(table_name)
        if 'insert' in policy_types:
            table_results['insert'] = executor.apply_insert_policy(table_name)
        if 'update' in policy_types:
            table_results['update'] = executor.apply_update_policy(table_name)
        if 'delete' in policy_types:
            table_results['delete'] = executor.apply_delete_policy(table_name)
    
    results[table_name] = table_results
    
    # Check if all policies were applied successfully
    all_success = all(
        success if isinstance(success, bool) else all(success.values())
        for success in results.values()
    )
    
    if all_success:
        vcprint(f"Successfully applied all policies to {table_name}!", color='green')
    else:
        vcprint(f"Some policies failed to apply to {table_name}. Check results for details.", color='yellow')
    
    return results


if __name__ == "__main__":
    # Simple variable declarations
    table_name = "scrape_domain"  # This is the ONLY table that will be affected
    database_project = "supabase_automation_matrix"
    policy_types = None  # None for all policies, or list like ['view', 'update']
    
    # Call the function with these arguments
    results = apply_policies(
        table_name=table_name,  # ONLY this table will be modified
        database_project=database_project,
        policy_types=policy_types
    )
    
    # Print results summary
    vcprint(data=results, title=f'Policy Results for {table_name} ONLY', pretty=True, verbose=True, color='blue')