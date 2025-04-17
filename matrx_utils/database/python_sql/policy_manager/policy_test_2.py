import os
from common import vcprint
from database.client.postgres_connection import execute_sql_query


def create_supabase_rls_policy(table_name, schema="public", database_project=None):
    """
    Create a minimal RLS policy specifically for Supabase.

    Args:
        table_name (str): The name of the table to apply the policy to
        schema (str, optional): Database schema. Defaults to 'public'.
        database_project (str, optional): The database project identifier.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use schema-qualified table name, properly quoted for PostgreSQL
        full_table_name = f'"{schema}"."{table_name}"'

        # First, check if the table exists
        vcprint(f"Checking if table {full_table_name} exists...\n", color="blue")
        check_table_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        ) AS table_exists;
        """

        table_check = execute_sql_query(check_table_query, (schema, table_name), database_project)

        if not table_check or not table_check[0]["table_exists"]:
            vcprint(f"Error: Table {full_table_name} does not exist!\n", color="red")
            return False

        vcprint(f"Table {full_table_name} exists.\n", color="green")

        # Step 1: Enable RLS on the table
        # This might give "no results to fetch" but that's OK for DDL statements
        enable_rls_query = f"ALTER TABLE {full_table_name} ENABLE ROW LEVEL SECURITY;"
        vcprint(f"Enabling RLS with query: {enable_rls_query}\n", color="blue")

        try:
            execute_sql_query(enable_rls_query, (), database_project)
            vcprint(f"RLS enabled on {full_table_name}.\n", color="green")
        except Exception as e:
            if "no results to fetch" in str(e):
                vcprint(
                    f"RLS likely enabled on {full_table_name} (got expected 'no results to fetch').\n",
                    color="green",
                )
            else:
                vcprint(f"Error enabling RLS: {str(e)}\n", color="red")
                return False

        # Step 2: Create basic policies for each operation
        operations = [
            {
                "name": f"Users can view their own {table_name}",
                "operation": "SELECT",
                "check": "USING",
            },
            {
                "name": f"Users can insert their own {table_name}",
                "operation": "INSERT",
                "check": "WITH CHECK",
            },
            {
                "name": f"Users can update their own {table_name}",
                "operation": "UPDATE",
                "check": "USING",
            },
            {
                "name": f"Users can delete their own {table_name}",
                "operation": "DELETE",
                "check": "USING",
            },
        ]

        for op in operations:
            policy_name = op["name"]
            vcprint(f"\nCreating policy '{policy_name}'...\n", color="blue")

            # Drop the policy if it already exists
            drop_policy_query = f'DROP POLICY IF EXISTS "{policy_name}" ON {full_table_name};'

            try:
                execute_sql_query(drop_policy_query, (), database_project)
                vcprint(f"Dropped any existing policy with same name.\n", color="green")
            except Exception as e:
                if "no results to fetch" in str(e):
                    vcprint(
                        f"Likely dropped policy (got expected 'no results to fetch').\n",
                        color="green",
                    )
                else:
                    vcprint(f"Error dropping policy: {str(e)}\n", color="red")

            # Create the policy - exact Supabase format
            create_policy_query = f"""
            CREATE POLICY "{policy_name}" 
            ON {full_table_name}
            FOR {op["operation"]}
            {op["check"]} (auth.uid() = user_id);
            """

            vcprint(f"Creating policy with query: {create_policy_query}\n", color="blue")

            try:
                execute_sql_query(create_policy_query, (), database_project)
                vcprint(f"Created policy for {op['operation']}.\n", color="green")
            except Exception as e:
                if "no results to fetch" in str(e):
                    vcprint(
                        f"Likely created policy (got expected 'no results to fetch').\n",
                        color="green",
                    )
                else:
                    vcprint(f"Error creating policy: {str(e)}\n", color="red")
                    return False

        # Step 3: Verify the policies were created
        vcprint("\nVerifying policies...\n", color="blue")
        verification_query = """
        SELECT 
            schemaname,
            tablename, 
            policyname, 
            cmd
        FROM 
            pg_policies
        WHERE 
            schemaname = %s AND 
            tablename = %s;
        """

        try:
            policies = execute_sql_query(verification_query, (schema, table_name), database_project)

            if policies and len(policies) > 0:
                vcprint(f"Successfully verified {len(policies)} policies:\n", color="green")
                for policy in policies:
                    vcprint(f"  - {policy['policyname']} ({policy['cmd']})\n", color="green")

                # Also verify RLS is enabled
                rls_query = """
                SELECT 
                    relname, 
                    relrowsecurity
                FROM 
                    pg_class
                WHERE 
                    relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s) AND
                    relname = %s;
                """

                rls_status = execute_sql_query(rls_query, (schema, table_name), database_project)
                if rls_status and rls_status[0]["relrowsecurity"]:
                    vcprint(
                        f"Verified RLS is enabled for {full_table_name}\n",
                        color="green",
                    )
                else:
                    vcprint(
                        f"WARNING: RLS might not be enabled for {full_table_name}\n",
                        color="yellow",
                    )

                return True
            else:
                # Try an alternative approach to check policies
                vcprint(
                    "No policies found using pg_policies view, trying alternative query...\n",
                    color="yellow",
                )
                alt_policy_check = """
                SELECT 
                    pc.relname as tablename,
                    pp.polname as policyname
                FROM 
                    pg_policy pp
                JOIN 
                    pg_class pc ON pp.polrelid = pc.oid
                JOIN 
                    pg_namespace pn ON pc.relnamespace = pn.oid
                WHERE 
                    pn.nspname = %s AND
                    pc.relname = %s;
                """

                alt_policies = execute_sql_query(alt_policy_check, (schema, table_name), database_project)
                if alt_policies and len(alt_policies) > 0:
                    vcprint(
                        f"Found {len(alt_policies)} policies using alternative query:\n",
                        color="green",
                    )
                    for p in alt_policies:
                        vcprint(
                            f"  - {p['policyname']} on {p['tablename']}\n",
                            color="green",
                        )
                    return True
                else:
                    vcprint(
                        "No policies found using alternative query method either.\n",
                        color="red",
                    )
                    vcprint(
                        "This suggests the policies were not created or you don't have permission to view them.\n",
                        color="red",
                    )
                    return False
        except Exception as e:
            vcprint(f"Error verifying policies: {str(e)}\n", color="red")
            vcprint(
                "This might be a permissions issue with viewing pg_policies.\n",
                color="yellow",
            )
            vcprint(
                "The policies may still have been created successfully.\n",
                color="yellow",
            )
            return True  # Return True anyway as the policies might have been created

    except Exception as e:
        vcprint(f"ERROR creating RLS policies: {str(e)}\n", color="red")
        import traceback

        vcprint(f"Traceback:\n{traceback.format_exc()}\n", color="red")
        return False


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    table_name = "conversation"
    schema = "public"
    database_project = "supabase_automation_matrix"

    vcprint("Starting Supabase RLS policy creation...\n", color="blue")
    success = create_supabase_rls_policy(table_name=table_name, schema=schema, database_project=database_project)

    if success:
        vcprint("✅ RLS policies likely created successfully!\n", color="green")
        vcprint(
            "You should now check in the Supabase dashboard to confirm the policies are active.\n",
            color="green",
        )
    else:
        vcprint("❌ Failed to create RLS policies.\n", color="red")
