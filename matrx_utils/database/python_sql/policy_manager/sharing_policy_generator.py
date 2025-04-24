import os
from common.utils.fancy_prints import vcprint
from database.client.postgres_connection import execute_sql_query


def add_sharing_to_table(table_name, schema="public", database_project=None):
    """
    Add sharing capabilities to a table that already has basic RLS policies.

    Args:
        table_name (str): The name of the table to modify
        schema (str, optional): Database schema. Defaults to 'public'.
        database_project (str, optional): The database project identifier.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First check if the permissions system is set up
        check_permissions_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'permissions'
        ) AS permissions_exists;
        """
        result = execute_sql_query(check_permissions_query, (schema,), database_project)

        if not result or not result[0]["permissions_exists"]:
            vcprint(
                "Error: Permissions table doesn't exist. Run setup_permissions_system first.\n",
                color="red",
            )
            return False

        # Check if the table exists
        check_table_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        ) AS table_exists;
        """
        result = execute_sql_query(check_table_query, (schema, table_name), database_project)

        if not result or not result[0]["table_exists"]:
            vcprint(f"Error: Table {schema}.{table_name} does not exist.\n", color="red")
            return False

        # Check if the resource_type enum includes this table
        check_resource_type_query = """
        SELECT EXISTS (
            SELECT 1 
            FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'resource_type') 
            AND enumlabel = %s
        ) AS value_exists;
        """
        result = execute_sql_query(check_resource_type_query, (table_name,), database_project)

        if not result or not result[0]["value_exists"]:
            # Add the table name to the resource_type enum
            vcprint(f"Adding {table_name} to resource_type enum...\n", color="yellow")
            add_enum_query = f"ALTER TYPE resource_type ADD VALUE IF NOT EXISTS '{table_name}';"
            try:
                execute_sql_query(add_enum_query, (), database_project)
                vcprint(f"Added {table_name} to resource_type enum.\n", color="green")
            except Exception as e:
                vcprint(
                    f"Error adding {table_name} to resource_type enum: {str(e)}\n",
                    color="red",
                )
                return False

        # All of our tables use user_id as the owner column
        owner_column = "user_id"

        # Use schema-qualified table name
        full_table_name = f'"{schema}"."{table_name}"'

        # Modify the SELECT policy to include shared items
        vcprint("Updating SELECT policy to include shared items...\n", color="yellow")
        select_policy_name = f"Users can view their own or shared {table_name}"
        drop_select_policy = f'DROP POLICY IF EXISTS "{select_policy_name}" ON {full_table_name};'

        try:
            execute_sql_query(drop_select_policy, (), database_project)
        except Exception as e:
            vcprint(f"Note: No existing sharing policy to drop: {str(e)}\n", color="yellow")

        create_select_policy = f"""
        CREATE POLICY "{select_policy_name}"
        ON {full_table_name}
        TO public
        FOR SELECT
        USING (
            (auth.uid() = {owner_column})
            OR 
            EXISTS (
                SELECT 1 FROM {schema}.permissions 
                WHERE resource_type = '{table_name}'::resource_type 
                AND resource_id = id
                AND (
                    -- Direct permission
                    (granted_to_user_id = auth.uid())
                    OR
                    -- Organization permission
                    (granted_to_organization_id IN (
                        SELECT organization_id FROM {schema}.organization_members 
                        WHERE user_id = auth.uid()
                    ))
                    OR
                    -- Public access
                    (is_public = TRUE)
                )
            )
        );
        """

        try:
            execute_sql_query(create_select_policy, (), database_project)
            vcprint(f"Created enhanced SELECT policy for {full_table_name}\n", color="green")
        except Exception as e:
            vcprint(f"Error creating enhanced SELECT policy: {str(e)}\n", color="red")
            vcprint(f"Failed SQL: {create_select_policy}\n", color="yellow")
            return False

        # Modify the UPDATE policy to include edit permissions
        vcprint("Updating UPDATE policy to include edit permissions...\n", color="yellow")
        update_policy_name = f"Users can update their own or editable {table_name}"
        drop_update_policy = f'DROP POLICY IF EXISTS "{update_policy_name}" ON {full_table_name};'

        try:
            execute_sql_query(drop_update_policy, (), database_project)
        except Exception as e:
            vcprint(
                f"Note: No existing update sharing policy to drop: {str(e)}\n",
                color="yellow",
            )

        create_update_policy = f"""
        CREATE POLICY "{update_policy_name}"
        ON {full_table_name}
        TO public
        FOR UPDATE
        USING (
            (auth.uid() = {owner_column})
            OR 
            EXISTS (
                SELECT 1 FROM {schema}.permissions 
                WHERE resource_type = '{table_name}'::resource_type 
                AND resource_id = id
                AND (
                    -- Direct permission
                    (granted_to_user_id = auth.uid() AND permission_level IN ('editor', 'admin'))
                    OR
                    -- Organization permission
                    (granted_to_organization_id IN (
                        SELECT organization_id FROM {schema}.organization_members 
                        WHERE user_id = auth.uid()
                    ) AND permission_level IN ('editor', 'admin'))
                )
            )
        );
        """

        try:
            execute_sql_query(create_update_policy, (), database_project)
            vcprint(f"Created enhanced UPDATE policy for {full_table_name}\n", color="green")
        except Exception as e:
            vcprint(f"Error creating enhanced UPDATE policy: {str(e)}\n", color="red")
            return False

        # Modify the DELETE policy to include admin permissions
        vcprint("Updating DELETE policy to include admin permissions...\n", color="yellow")
        delete_policy_name = f"Users can delete their own or administrable {table_name}"
        drop_delete_policy = f'DROP POLICY IF EXISTS "{delete_policy_name}" ON {full_table_name};'

        try:
            execute_sql_query(drop_delete_policy, (), database_project)
        except Exception as e:
            vcprint(
                f"Note: No existing delete sharing policy to drop: {str(e)}\n",
                color="yellow",
            )

        create_delete_policy = f"""
        CREATE POLICY "{delete_policy_name}"
        ON {full_table_name}
        TO public
        FOR DELETE
        USING (
            (auth.uid() = {owner_column})
            OR 
            EXISTS (
                SELECT 1 FROM {schema}.permissions 
                WHERE resource_type = '{table_name}'::resource_type 
                AND resource_id = id
                AND (
                    -- Direct permission
                    (granted_to_user_id = auth.uid() AND permission_level = 'admin')
                    OR
                    -- Organization permission
                    (granted_to_organization_id IN (
                        SELECT organization_id FROM {schema}.organization_members 
                        WHERE user_id = auth.uid()
                    ) AND permission_level = 'admin')
                )
            )
        );
        """

        try:
            execute_sql_query(create_delete_policy, (), database_project)
            vcprint(f"Created enhanced DELETE policy for {full_table_name}\n", color="green")
        except Exception as e:
            vcprint(f"Error creating enhanced DELETE policy: {str(e)}\n", color="red")
            return False

        # Create trigger to clean up permissions when resource is deleted
        vcprint("Creating cleanup trigger...\n", color="yellow")
        trigger_function_name = f"delete_{table_name}_permissions"

        create_trigger_function = f"""
        CREATE OR REPLACE FUNCTION {schema}.{trigger_function_name}()
        RETURNS TRIGGER AS $$
        BEGIN
          DELETE FROM {schema}.permissions 
          WHERE resource_type = '{table_name}'::resource_type 
          AND resource_id = OLD.id;
          RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
        """

        try:
            execute_sql_query(create_trigger_function, (), database_project)
            vcprint(f"Created trigger function for {full_table_name}\n", color="green")
        except Exception as e:
            vcprint(f"Error creating trigger function: {str(e)}\n", color="red")
            return False

        trigger_name = f"trigger_delete_{table_name}_permissions"
        drop_trigger = f"DROP TRIGGER IF EXISTS {trigger_name} ON {full_table_name};"

        try:
            execute_sql_query(drop_trigger, (), database_project)
        except Exception as e:
            vcprint(f"Note: No existing trigger to drop: {str(e)}\n", color="yellow")

        create_trigger = f"""
        CREATE TRIGGER {trigger_name}
        AFTER DELETE ON {full_table_name}
        FOR EACH ROW
        EXECUTE FUNCTION {schema}.{trigger_function_name}();
        """

        try:
            execute_sql_query(create_trigger, (), database_project)
            vcprint(f"Created trigger for {full_table_name}\n", color="green")
        except Exception as e:
            vcprint(f"Error creating trigger: {str(e)}\n", color="red")
            return False

        # Verify the policies
        verification_query = """
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
            tablename = %s AND
            policyname ILIKE '%%shared%%'
        ORDER BY 
            policyname;
        """

        policies = execute_sql_query(verification_query, (schema, table_name), database_project)

        if policies and len(policies) > 0:
            vcprint(
                f"Successfully applied sharing policies to {full_table_name}\n",
                color="green",
            )
            vcprint(f"Verified {len(policies)} sharing policies:\n", color="green")
            for policy in policies:
                vcprint(f"  - {policy['policyname']} ({policy['cmd']})\n", color="green")

            # Verify trigger exists
            trigger_query = """
            SELECT 
                tgname, 
                tgenabled
            FROM 
                pg_trigger
            WHERE 
                tgrelid = %s::regclass AND
                tgname = %s;
            """

            trigger_status = execute_sql_query(trigger_query, (full_table_name, trigger_name), database_project)

            if trigger_status and len(trigger_status) > 0:
                vcprint(f"Verified trigger is set up for {full_table_name}\n", color="green")
            else:
                vcprint(
                    f"WARNING: Trigger doesn't appear to be set up correctly for {full_table_name}\n",
                    color="red",
                )

            return True
        else:
            vcprint(
                f"Failed to verify sharing policies for {full_table_name}.\n",
                color="red",
            )
            return False
    except Exception as e:
        vcprint(f"\nError adding sharing to {table_name}: {str(e)}\n", color="red")
        return False


if __name__ == "__main__":
    os.system("cls")
    table_name = "scrape_domain"
    schema = "public"
    database_project = "supabase_automation_matrix"
    success = add_sharing_to_table(table_name, schema=schema, database_project=database_project)
