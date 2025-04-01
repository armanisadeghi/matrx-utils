from database.python_sql.db_objects import get_db_objects
from datetime import datetime, timedelta, timezone


def get_tables_and_views_list(schema='public', details=False):
    """
    Returns information about tables and views.

    If details is False, returns a simple list of table and view names.
    If details is True, returns the full information for each object.
    """
    objects = get_db_objects(schema)
    if details:
        return objects
    return [obj['name'] for obj in objects]


def get_tables(schema='public', details=False):
    """
    Returns information about tables only.

    If details is False, returns a simple list of table names.
    If details is True, returns the full information for each table.
    """
    objects = [obj for obj in get_db_objects(schema) if obj['type'] == 'table']
    if details:
        return objects
    return [obj['name'] for obj in objects]


def get_views(schema='public', details=False):
    """
    Returns information about views only.

    If details is False, returns a simple list of view names.
    If details is True, returns the full information for each view.
    """
    objects = [obj for obj in get_db_objects(schema) if obj['type'] == 'view']
    if details:
        return objects
    return [obj['name'] for obj in objects]


def get_row_analysis(schema='public', row_threshold=1000):
    """
    Returns a list of tables that might need indexing based on row count.

    Parameters:
    - schema: The database schema to analyze
    - row_threshold: The minimum number of rows a table should have to be considered for indexing

    Returns a list of dictionaries containing:
    - name: Table name
    - rows: Number of rows
    - size_bytes: Table size in bytes
    - index_size_bytes: Total size of indexes on the table
    - index_ratio: Ratio of index size to table size
    """
    tables = get_tables(schema, details=True)
    analysis = []
    for table in tables:
        if table['rows'] is not None and table['rows'] >= row_threshold:
            index_ratio = table['index_size_bytes'] / table['size_bytes'] if table['size_bytes'] > 0 else 0
            analysis.append({
                'name': table['name'],
                'rows': table['rows'],
                'size_bytes': table['size_bytes'],
                'index_size_bytes': table['index_size_bytes'],
                'index_ratio': index_ratio
            })
    return sorted(analysis, key=lambda x: x['rows'], reverse=True)


def get_stale_statistics(schema='public', days_threshold=7):
    """
    Returns a list of tables with potentially stale statistics.

    Parameters:
    - schema: The database schema to analyze
    - days_threshold: Number of days since last ANALYZE to consider statistics as stale

    Returns a list of dictionaries containing:
    - name: Table name
    - rows: Number of rows
    - last_analyze: Timestamp of the last ANALYZE operation
    """
    tables = get_tables(schema, details=True)
    stale_tables = []
    threshold_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    for table in tables:
        last_analyze = table['last_analyze']
        if last_analyze is not None:
            last_analyze = last_analyze.replace(tzinfo=timezone.utc)
        if last_analyze is None or last_analyze < threshold_date:
            stale_tables.append({
                'name': table['name'],
                'rows': table['rows'],
                'last_analyze': last_analyze
            })
    return sorted(stale_tables, key=lambda x: x['rows'] if x['rows'] is not None else 0, reverse=True)


if __name__ == '__main__':
    from common import vcprint

    schema = 'public'

    vcprint(data=get_tables_and_views_list(schema), title='All Tables and Views (Simple List)', pretty=True, verbose=True, color='blue')
    vcprint(data=get_tables_and_views_list(schema, details=True), title='All Tables and Views (Detailed)', pretty=True, verbose=True, color='blue')

    vcprint(data=get_tables(schema), title='Tables Only (Simple List)', pretty=True, verbose=True, color='green')
    vcprint(data=get_tables(schema, details=True), title='Tables Only (Detailed)', pretty=True, verbose=True, color='green')

    vcprint(data=get_views(schema), title='Views Only (Simple List)', pretty=True, verbose=True, color='yellow')
    vcprint(data=get_views(schema, details=True), title='Views Only (Detailed)', pretty=True, verbose=True, color='yellow')

    vcprint(data=get_row_analysis(schema), title='Tables Potentially Needing Indexing', pretty=True, verbose=True, color='red')
    vcprint(data=get_stale_statistics(schema), title='Tables with Potentially Stale Statistics', pretty=True, verbose=True, color='magenta')
