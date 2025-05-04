# matrx_utils\database\python_sql\policy_manager\policy_test_3.py
from database.client.postgres_connection import execute_sql_query


def check_all_policies(database_project=None):
    """Check if any RLS policies exist in the database."""
    query = """
    SELECT schemaname, tablename, policyname, cmd 
    FROM pg_policies 
    LIMIT 100;
    """

    try:
        policies = execute_sql_query(query, (), database_project)
        print(f"Found {len(policies)} policies in the database:")
        for policy in policies:
            print(f"  {policy['schemaname']}.{policy['tablename']}: {policy['policyname']} ({policy['cmd']})")
        return policies
    except Exception as e:
        print(f"Error checking policies: {str(e)}")
        return []


if __name__ == "__main__":
    check_all_policies(database_project="supabase_automation_matrix")
