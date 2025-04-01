import os
from typing import List, Optional, Dict
from database.client.postgres_connection import get_postgres_connection
from common import vcprint

class PolicyManager:
    def __init__(self, database_project: str):
        self.database_project = database_project
    
    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> bool:
        print(f"Executing SQL on {self.database_project}:")
        print(f"{sql[:200]}..." if len(sql) > 200 else sql)
        
        conn = get_postgres_connection(self.database_project)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error executing SQL: {e}")
            return False
        finally:
            # Return connection to pool is handled by get_postgres_connection
            conn.close()
    
    def drop_table_policies(self, table_name: str) -> bool:
        sql = f"""
DO $$
DECLARE
    policy_name text;
BEGIN
    FOR policy_name IN 
        SELECT policyname 
        FROM pg_policies 
        WHERE tablename = '{table_name}' 
        AND schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY %I ON public.{table_name}', policy_name);
    END LOOP;
END
$$;
        """
        return self.execute_sql(sql)
    
    def generate_view_policy(self, table_name: str) -> str:
        return f"""
CREATE POLICY "Users can view permitted {table_name}" 
ON public.{table_name} 
FOR SELECT 
TO authenticated 
USING (
  auth_has_access(auth.uid(), '{table_name}'::resource_type, id, 'viewer')
);
        """
    
    def generate_insert_policy(self, table_name: str) -> str:
        return f"""
CREATE POLICY "Users can insert {table_name}" 
ON public.{table_name} 
FOR INSERT 
TO authenticated 
WITH CHECK (
  auth_has_access(auth.uid(), '{table_name}'::resource_type, id, 'editor')
);
        """
    
    def generate_update_policy(self, table_name: str) -> str:
        return f"""
CREATE POLICY "Users can update permitted {table_name}" 
ON public.{table_name} 
FOR UPDATE 
TO authenticated 
USING (
  auth_has_access(auth.uid(), '{table_name}'::resource_type, id, 'editor')
);
        """
    
    def generate_delete_policy(self, table_name: str) -> str:
        return f"""
CREATE POLICY "Users can delete permitted {table_name}" 
ON public.{table_name} 
FOR DELETE 
TO authenticated 
USING (
  auth_has_access(auth.uid(), '{table_name}'::resource_type, id, 'admin')
);
        """
    
    def apply_view_policy(self, table_name: str) -> bool:
        sql = self.generate_view_policy(table_name)
        return self.execute_sql(sql)
    
    def apply_insert_policy(self, table_name: str) -> bool:
        sql = self.generate_insert_policy(table_name)
        return self.execute_sql(sql)
    
    def apply_update_policy(self, table_name: str) -> bool:
        sql = self.generate_update_policy(table_name)
        return self.execute_sql(sql)
    
    def apply_delete_policy(self, table_name: str) -> bool:
        sql = self.generate_delete_policy(table_name)
        return self.execute_sql(sql)
    
    def apply_table_policies(self, table_name: str, drop_existing: bool = True, policy_types: Optional[List[str]] = None) -> Dict[str, bool]:
        if policy_types is None:
            policy_types = ['view', 'insert', 'update', 'delete']
        
        results = {}
        
        # Drop existing policies if requested (but ONLY for this specific table)
        if drop_existing:
            vcprint(f"Dropping all existing policies for table: {table_name}", color='green')
            drop_result = self.drop_table_policies(table_name)
            results['drop'] = drop_result
        
        # Apply requested policies
        if 'view' in policy_types:
            vcprint(f"Applying view policy to {table_name}", color='green')
            results['view'] = self.apply_view_policy(table_name)
        
        if 'insert' in policy_types:
            vcprint(f"Applying insert policy to {table_name}", color='green')
            results['insert'] = self.apply_insert_policy(table_name)
        
        if 'update' in policy_types:
            vcprint(f"Applying update policy to {table_name}", color='green')
            results['update'] = self.apply_update_policy(table_name)
        
        if 'delete' in policy_types:
            vcprint(f"Applying delete policy to {table_name}", color='green')
            results['delete'] = self.apply_delete_policy(table_name)
        
        return results


def apply_policies(table_name: str, database_project: str, drop_existing: bool = True, policy_types: Optional[List[str]] = None):
    manager = PolicyManager(database_project)
    results = manager.apply_table_policies(table_name, drop_existing, policy_types)
    
    # Print final results
    all_success = all(results.values())
    if all_success:
        vcprint(f"Successfully applied all policies to {table_name}!", color='green')
    else:
        vcprint(f"Some policy operations failed for {table_name}. Check results for details.", color='yellow')
    
    return results


if __name__ == "__main__":
    os.system("cls")
    table_name = "scrape_domain"
    database_project = "supabase_automation_matrix"
    drop_existing = True  # Whether to drop existing policies first
    policy_types = None  # ['view', 'update', 'insert', 'delete'] or None for all
    
    results = apply_policies(
        table_name=table_name,
        database_project=database_project,
        drop_existing=drop_existing,
        policy_types=policy_types
    )
    
    vcprint(data=results, title=f'Policy Results for {table_name}', pretty=True, verbose=True, color='blue')