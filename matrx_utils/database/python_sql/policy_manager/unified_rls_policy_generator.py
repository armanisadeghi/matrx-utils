# matrx_utils\database\python_sql\policy_manager\unified_rls_policy_generator.py
import os
from common.utils.fancy_prints import vcprint
from database.client.postgres_connection import execute_sql_query


def set_unified_rls_policy(table_name, schema="public", database_project=None):
    """
    Apply consistent Row Level Security policies to a specified table using
    explicit transaction blocks.

    Args:
        table_name (str): The name of the table to apply RLS policies to
        schema (str, optional): Database schema. Defaults to 'public'.
        database_project (str, optional): The database project identifier.

    Returns:
        bool: True if successful, False otherwise
    """
    # All of our tables use user_id as the owner column
    owner_column = "user_id"

    # Use the table name as the resource type name
    resource_type_name = table_name

    # Standard insertion check
    insertion_check = "auth.uid() = user_id"

    # Use schema-qualified table name with quotes (Supabase style)
    full_table_name = f'"{schema}"."{table_name}"'

    # Generate the SQL query with explicit transaction blocks
    query = f"""
BEGIN;

-- =======================================
-- ENABLE ROW LEVEL SECURITY
-- =======================================
ALTER TABLE {full_table_name} ENABLE ROW LEVEL SECURITY;

-- =======================================
-- BASIC POLICIES FOR SELECT/INSERT/UPDATE/DELETE
-- =======================================

-- Drop existing policies first
DROP POLICY IF EXISTS "{table_name}_select_policy" ON {full_table_name};
DROP POLICY IF EXISTS "{table_name}_insert_policy" ON {full_table_name};
DROP POLICY IF EXISTS "{table_name}_update_policy" ON {full_table_name};
DROP POLICY IF EXISTS "{table_name}_delete_policy" ON {full_table_name};

-- SELECT policy: Can view if user has at least viewer access
CREATE POLICY "{table_name}_select_policy" 
ON {full_table_name} 
FOR SELECT 
USING (
  -- Direct ownership
  {owner_column} = auth.uid()
  OR
  -- Via permissions system
  auth_has_access(auth.uid(), '{resource_type_name}'::resource_type, id, 'viewer'::permission_level)
);

-- INSERT policy: Can create new records if they pass the insertion check
CREATE POLICY "{table_name}_insert_policy" 
ON {full_table_name} 
FOR INSERT 
WITH CHECK ({insertion_check});

-- UPDATE policy: Can update if user has at least editor access
CREATE POLICY "{table_name}_update_policy" 
ON {full_table_name} 
FOR UPDATE 
USING (
  -- Direct ownership
  {owner_column} = auth.uid()
  OR
  -- Via permissions system
  auth_has_access(auth.uid(), '{resource_type_name}'::resource_type, id, 'editor'::permission_level)
);

-- DELETE policy: Can delete if user has admin access
CREATE POLICY "{table_name}_delete_policy" 
ON {full_table_name} 
FOR DELETE 
USING (
  -- Direct ownership
  {owner_column} = auth.uid()
  OR
  -- Via permissions system
  auth_has_access(auth.uid(), '{resource_type_name}'::resource_type, id, 'admin'::permission_level)
);

-- =======================================
-- CREATE TRIGGER TO HANDLE PERMISSION CLEANUP
-- =======================================

-- This creates a trigger function that will automatically remove
-- permissions records when a resource is deleted
CREATE OR REPLACE FUNCTION {schema}.delete_{table_name}_permissions()
RETURNS TRIGGER AS $$
BEGIN
  DELETE FROM permissions 
  WHERE resource_type = '{resource_type_name}'::resource_type 
  AND resource_id = OLD.id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- This attaches the trigger function to the table
DROP TRIGGER IF EXISTS trigger_delete_{table_name}_permissions ON {full_table_name};

CREATE TRIGGER trigger_delete_{table_name}_permissions
AFTER DELETE ON {full_table_name}
FOR EACH ROW
EXECUTE FUNCTION {schema}.delete_{table_name}_permissions();

COMMIT;

-- Return a dummy result to avoid "no results to fetch" error
SELECT 'RLS policies applied successfully to {full_table_name}' AS result;
"""

    try:
        # Execute the query using your existing function
        result = execute_sql_query(query, (), database_project)

        # Verify the policies were created
        verification_query = f"""
        SELECT 
            tablename, 
            policyname, 
            cmd
        FROM 
            pg_policies
        WHERE 
            schemaname = %s AND 
            tablename = %s
        ORDER BY 
            policyname;
        """

        policies = execute_sql_query(verification_query, (schema, table_name), database_project)

        if policies and len(policies) >= 4:  # We expect at least 4 policies (SELECT, INSERT, UPDATE, DELETE)
            print(f"Successfully applied RLS policies to {full_table_name}")
            print(f"Verified {len(policies)} policies:")
            for policy in policies:
                print(f"  - {policy['policyname']} ({policy['cmd']})")
            return True
        else:
            print(f"Failed to verify policies for {full_table_name}. Found {len(policies) if policies else 0} policies.")
            if policies:
                for policy in policies:
                    print(f"  - {policy['policyname']} ({policy['cmd']})")
            return False
    except Exception as e:
        print(f"Error applying or verifying RLS policies to {full_table_name}: {str(e)}")
        return False


if __name__ == "__main__":
    os.system("cls")
    table_name = "scrape_domain"
    schema = "public"
    database_project = "supabase_automation_matrix"
    success = set_unified_rls_policy(table_name, schema=schema, database_project=database_project)
