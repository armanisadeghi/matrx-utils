# matrx_utils\database\python_sql\policy_manager\python_test_3.py
from database.client.postgres_connection import execute_sql_query
import time


def diagnose_policy_creation(table_name, schema="public", database_project=None):
    """
    Comprehensive diagnostic function to troubleshoot policy creation issues.

    Args:
        table_name (str): The name of the table to test
        schema (str, optional): Database schema. Defaults to 'public'.
        database_project (str, optional): The database project identifier.

    Returns:
        dict: Diagnostic results
    """
    results = {
        "table_exists": False,
        "rls_enabled": False,
        "existing_policies": [],
        "creation_attempts": [],
        "dashboard_policies": [],
    }

    print(f"==== STARTING COMPREHENSIVE POLICY DIAGNOSTICS FOR {schema}.{table_name} ====")

    # Check if table exists
    table_check_query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = %s 
        AND table_name = %s
    ) AS table_exists;
    """

    try:
        table_check_result = execute_sql_query(table_check_query, (schema, table_name), database_project)
        if not table_check_result or not table_check_result[0]["table_exists"]:
            print(f"ERROR: Table {schema}.{table_name} does not exist!")
            return results

        results["table_exists"] = True
        print(f"✓ Table {schema}.{table_name} exists.")

        # Check if RLS is enabled
        rls_check_query = """
        SELECT c.relname, c.relrowsecurity
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = %s AND c.relname = %s;
        """

        rls_check = execute_sql_query(rls_check_query, (schema, table_name), database_project)
        if rls_check and rls_check[0]["relrowsecurity"]:
            results["rls_enabled"] = True
            print(f"✓ RLS is already enabled on {schema}.{table_name}.")
        else:
            print(f"Enabling RLS on {schema}.{table_name}...")
            enable_rls_query = f"""
            ALTER TABLE "{schema}"."{table_name}" ENABLE ROW LEVEL SECURITY;
            SELECT 'RLS enabled' AS result;
            """

            execute_sql_query(enable_rls_query, (), database_project)

            # Verify RLS was enabled
            rls_check = execute_sql_query(rls_check_query, (schema, table_name), database_project)
            if rls_check and rls_check[0]["relrowsecurity"]:
                results["rls_enabled"] = True
                print(f"✓ RLS successfully enabled on {schema}.{table_name}.")
            else:
                print(f"✗ Failed to enable RLS on {schema}.{table_name}.")

        # Check existing policies
        policy_check_query = """
        SELECT 
            tablename, 
            policyname, 
            cmd, 
            qual,
            with_check
        FROM 
            pg_policies
        WHERE 
            schemaname = %s AND 
            tablename = %s;
        """

        existing_policies = execute_sql_query(policy_check_query, (schema, table_name), database_project)
        if existing_policies and len(existing_policies) > 0:
            results["existing_policies"] = existing_policies
            print(f"Found {len(existing_policies)} existing policies for {schema}.{table_name}:")
            for policy in existing_policies:
                print(f"  - {policy['policyname']} ({policy['cmd']})")
        else:
            print(f"No existing policies found for {schema}.{table_name}.")

        # ======= Try multiple policy creation methods =======

        # Method 1: Standard SQL syntax with qualified table name
        policy_name_1 = f"test_policy_standard_{int(time.time())}"
        print(f"\nMethod 1: Trying standard SQL syntax with qualified table name...")
        creation_query_1 = f"""
        CREATE POLICY "{policy_name_1}" 
        ON "{schema}"."{table_name}"
        USING (true);
        
        SELECT 'Policy created' AS result;
        """

        try:
            execute_sql_query(creation_query_1, (), database_project)
            print(f"✓ Command executed without errors.")
            results["creation_attempts"].append(
                {
                    "method": "standard_sql",
                    "policy_name": policy_name_1,
                    "executed_without_error": True,
                }
            )
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results["creation_attempts"].append(
                {
                    "method": "standard_sql",
                    "policy_name": policy_name_1,
                    "executed_without_error": False,
                    "error": str(e),
                }
            )

        # Method 2: Try with unquoted table name
        policy_name_2 = f"test_policy_unquoted_{int(time.time())}"
        print(f"\nMethod 2: Trying with unquoted table name...")
        creation_query_2 = f"""
        CREATE POLICY "{policy_name_2}" 
        ON {schema}.{table_name}
        USING (true);
        
        SELECT 'Policy created' AS result;
        """

        try:
            execute_sql_query(creation_query_2, (), database_project)
            print(f"✓ Command executed without errors.")
            results["creation_attempts"].append(
                {
                    "method": "unquoted_table",
                    "policy_name": policy_name_2,
                    "executed_without_error": True,
                }
            )
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results["creation_attempts"].append(
                {
                    "method": "unquoted_table",
                    "policy_name": policy_name_2,
                    "executed_without_error": False,
                    "error": str(e),
                }
            )

        # Method 3: Try specifying role and operation
        policy_name_3 = f"test_policy_role_op_{int(time.time())}"
        print(f"\nMethod 3: Trying with explicit role and operation...")
        creation_query_3 = f"""
        CREATE POLICY "{policy_name_3}" 
        ON "{schema}"."{table_name}"
        FOR SELECT
        TO authenticated
        USING (true);
        
        SELECT 'Policy created' AS result;
        """

        try:
            execute_sql_query(creation_query_3, (), database_project)
            print(f"✓ Command executed without errors.")
            results["creation_attempts"].append(
                {
                    "method": "explicit_role_op",
                    "policy_name": policy_name_3,
                    "executed_without_error": True,
                }
            )
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results["creation_attempts"].append(
                {
                    "method": "explicit_role_op",
                    "policy_name": policy_name_3,
                    "executed_without_error": False,
                    "error": str(e),
                }
            )

        # Method 4: Try with transaction block
        policy_name_4 = f"test_policy_transaction_{int(time.time())}"
        print(f"\nMethod 4: Trying with explicit transaction block...")
        creation_query_4 = f"""
        BEGIN;
        CREATE POLICY "{policy_name_4}" 
        ON "{schema}"."{table_name}"
        USING (true);
        COMMIT;
        
        SELECT 'Policy created with transaction' AS result;
        """

        try:
            execute_sql_query(creation_query_4, (), database_project)
            print(f"✓ Command executed without errors.")
            results["creation_attempts"].append(
                {
                    "method": "transaction",
                    "policy_name": policy_name_4,
                    "executed_without_error": True,
                }
            )
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results["creation_attempts"].append(
                {
                    "method": "transaction",
                    "policy_name": policy_name_4,
                    "executed_without_error": False,
                    "error": str(e),
                }
            )

        # ======= Check policies after creation attempts =======
        print("\nChecking for policies after creation attempts...")
        final_policies = execute_sql_query(policy_check_query, (schema, table_name), database_project)

        if final_policies and len(final_policies) > 0:
            new_policies = [p for p in final_policies if p not in existing_policies]
            results["dashboard_policies"] = final_policies

            if new_policies:
                print(f"✓ SUCCESS! Found {len(new_policies)} new policies:")
                for policy in new_policies:
                    print(f"  - {policy['policyname']} ({policy['cmd']})")
            else:
                print(f"✗ No new policies were created. Found same {len(final_policies)} existing policies.")
        else:
            print(f"✗ No policies found for {schema}.{table_name} after creation attempts.")

        # ======= Additional checks =======
        print("\nChecking current database settings...")

        # Check current transaction isolation level
        isolation_query = "SHOW transaction_isolation;"
        isolation = execute_sql_query(isolation_query, (), database_project)
        print(f"Transaction isolation: {isolation[0]['transaction_isolation']}")

        # Check if in a transaction
        transaction_query = "SELECT pg_current_xact_id() IS NOT NULL AS in_transaction;"
        transaction = execute_sql_query(transaction_query, (), database_project)
        print(f"In transaction: {transaction[0]['in_transaction']}")

        # Check current role and permissions
        role_query = """
        SELECT current_user, current_database(), 
               current_setting('role') as current_role_setting,
               has_table_privilege(current_user, %s, 'INSERT,SELECT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') as has_table_privileges,
               has_schema_privilege(current_user, %s, 'USAGE,CREATE') as has_schema_privileges;
        """
        role_info = execute_sql_query(role_query, (f"{schema}.{table_name}", schema), database_project)
        print(f"Current user: {role_info[0]['current_user']}")
        print(f"Database: {role_info[0]['current_database']}")
        print(f"Current role setting: {role_info[0]['current_role_setting']}")
        print(f"Has table privileges: {role_info[0]['has_table_privileges']}")
        print(f"Has schema privileges: {role_info[0]['has_schema_privileges']}")

        # Check for event triggers that might be intercepting policy creation
        trigger_query = """
        SELECT evtname, evtevent, evtenabled
        FROM pg_event_trigger;
        """

        try:
            triggers = execute_sql_query(trigger_query, (), database_project)
            if triggers and len(triggers) > 0:
                print(f"Found {len(triggers)} event triggers that may affect DDL operations:")
                for trigger in triggers:
                    print(f"  - {trigger['evtname']} ({trigger['evtevent']}, enabled: {trigger['evtenabled']})")
            else:
                print("No event triggers found.")
        except Exception as e:
            print(f"Error checking event triggers: {str(e)}")

        # Check for extensions
        extension_query = "SELECT extname FROM pg_extension;"
        extensions = execute_sql_query(extension_query, (), database_project)
        print(f"Installed extensions: {', '.join([ext['extname'] for ext in extensions])}")

    except Exception as e:
        print(f"ERROR during diagnostics: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        print(f"==== COMPLETED POLICY DIAGNOSTICS FOR {schema}.{table_name} ====")

    return results


if __name__ == "__main__":
    table_name = "scrape_domain"  # Use a table you know exists
    schema = "public"
    database_project = "supabase_automation_matrix"

    results = diagnose_policy_creation(table_name, schema=schema, database_project=database_project)
