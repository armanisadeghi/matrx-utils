import os
from common.utils.fancy_prints import vcprint
from database.client.postgres_connection import execute_sql_query


def set_unified_rls_policy(table_name, schema="public", database_project=None):
    """
    Apply consistent Row Level Security policies to a specified table using
    explicit transaction blocks and ensure the resource type exists in the enum.

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

    # First, check if the resource type exists in the enum and add it if not
    check_and_add_resource_type_query = f"""
    DO $$
    BEGIN
        -- Check if the type exists
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resource_type') THEN
            -- Check if the value exists in the enum
            IF NOT EXISTS (
                SELECT 1 
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = 'resource_type'
                AND e.enumlabel = '{resource_type_name}'
            ) THEN
                -- Add the value to the enum
                EXECUTE 'ALTER TYPE resource_type ADD VALUE IF NOT EXISTS '''{resource_type_name}'''';
                RAISE NOTICE 'Added %% to resource_type enum', '{resource_type_name}';
            ELSE
                RAISE NOTICE 'Resource type %% already exists in enum', '{resource_type_name}';
            END IF;
        ELSE
            RAISE EXCEPTION 'resource_type enum does not exist. Please set up the permissions system first.';
        END IF;
    END
    $$;
    
    -- Return a dummy result
    SELECT 'Resource type check completed' AS result;
    """

    # Generate the SQL query with explicit transaction blocks
    rls_query = f"""
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
        # First add the resource type to the enum if needed
        print(f"Checking and adding resource type '{resource_type_name}' to enum if needed...")
        enum_result = execute_sql_query(check_and_add_resource_type_query, (), database_project)

        # Then apply the RLS policies
        print(f"Applying RLS policies to {full_table_name}...")
        rls_result = execute_sql_query(rls_query, (), database_project)

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
            print(f"✅ Successfully applied RLS policies to {full_table_name}")
            print(f"✅ Verified {len(policies)} policies:")
            for policy in policies:
                print(f"  - {policy['policyname']} ({policy['cmd']})")

            # Verify that the enum value exists
            enum_check_query = """
            SELECT EXISTS (
                SELECT 1 
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = 'resource_type'
                AND e.enumlabel = %s
            ) as exists;
            """
            enum_exists = execute_sql_query(enum_check_query, (resource_type_name,), database_project)
            if enum_exists and enum_exists[0]["exists"]:
                print(f"✅ Verified '{resource_type_name}' exists in resource_type enum")
            else:
                print(f"❌ Failed to verify '{resource_type_name}' in resource_type enum")
                return False

            return True
        else:
            print(f"❌ Failed to verify policies for {full_table_name}. Found {len(policies) if policies else 0} policies.")
            if policies:
                for policy in policies:
                    print(f"  - {policy['policyname']} ({policy['cmd']})")
            return False
    except Exception as e:
        print(f"❌ Error applying or verifying RLS policies to {full_table_name}: {str(e)}")
        return False


def apply_rls_to_all_tables(tables, schema="public", database_project=None):
    """
    Apply RLS policies to multiple tables and report results.

    Args:
        tables (list): List of table names to apply RLS to
        schema (str, optional): Database schema. Defaults to 'public'.
        database_project (str, optional): The database project identifier.

    Returns:
        dict: Results showing success/failure for each table
    """
    results = {}
    total = len(tables)
    success_count = 0

    print(f"Applying RLS policies to {total} tables...")

    for i, table in enumerate(tables, 1):
        print(f"\n[{i}/{total}] Processing {table}...")
        success = set_unified_rls_policy(table, schema, database_project)
        results[table] = success
        if success:
            success_count += 1

    # Print summary
    print(f"\n{'='*50}")
    print(f"RLS POLICY APPLICATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total tables: {total}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total - success_count}")

    # List failures if any
    if total - success_count > 0:
        print("\nFailed tables:")
        for table, success in results.items():
            if not success:
                print(f"  - {table}")

    print(f"{'='*50}")

    return results


if __name__ == "__main__":
    os.system("cls")

    # Example of applying to a single table
    # table_name = "conversation"
    # schema = 'public'
    # database_project = 'supabase_automation_matrix'
    # success = set_unified_rls_policy(table_name, schema=schema, database_project=database_project)

    # Example of applying to multiple tables
    tables_to_secure = [
        "conversation",
        "message",
    ]

    schema = "public"
    database_project = "supabase_automation_matrix"

    results = apply_rls_to_all_tables(tables_to_secure, schema, database_project)
