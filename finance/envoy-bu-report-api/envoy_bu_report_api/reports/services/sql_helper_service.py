import re
import json


class SqlHelperService:
    @staticmethod
    def remove_skipped_columns_from_sql(sql, skip_columns):
        """
        Remove skipped columns from SQL SELECT clause
        
        Args:
            sql (str): Original SQL query
            skip_columns (list): List of columns to skip
            
        Returns:
            str: Modified SQL query
        """
        skip_codes = [col['code'] for col in skip_columns]
        
        # Remove from SELECT clause
        def replace_select(match):
            select_part = match.group(1)
            fields = re.split(r',(?![^()]*\))', select_part)
            
            filtered_fields = []
            for field in fields:
                should_include = True
                for code in skip_codes:
                    if (re.search(rf'\bAS\s+{code}\b', field, re.IGNORECASE) or
                        re.search(rf'\.{code}\b', field, re.IGNORECASE) or
                        re.search(rf'\b{code}\b', field, re.IGNORECASE)):
                        should_include = False
                        break
                if should_include:
                    filtered_fields.append(field)
            
            return 'SELECT ' + ', '.join(filtered_fields) + ' FROM '
        
        sql = re.sub(r'SELECT\s+(.*?)\s+FROM\s+', replace_select, sql, flags=re.IGNORECASE)
        return sql

    @staticmethod
    def apply_sort(sql, sort_by, sort_dir, allowed_columns):
        """
        Apply sorting to SQL query
        
        Args:
            sql (str): Original SQL query
            sort_by (str): Column to sort by
            sort_dir (str): Sort direction (ASC/DESC)
            allowed_columns (list): List of allowed columns for sorting
            
        Returns:
            str: Modified SQL query with ORDER BY
        """
        if not sort_by or sort_by not in allowed_columns:
            return sql
        
        sort_dir = sort_dir.upper() if sort_dir.upper() in ['ASC', 'DESC'] else 'ASC'
        
        # Remove existing ORDER BY
        sql = re.sub(r'ORDER\s+BY\s+[^)]*(?=(?:\)|$|\s+LIMIT|\s+OFFSET))', '', sql, flags=re.IGNORECASE)
        sql = sql.rstrip(" \t\n\r,")
        
        return f"{sql} ORDER BY {sort_by} {sort_dir}"

    @staticmethod
    def build_chart_where_clause(sql, filter_values, from_date=None, to_date=None, date_column=None):
        """
        Build WHERE clause for chart queries
        
        Args:
            sql (str): Original SQL query
            filter_values (dict): Filter values
            from_date (str): Start date
            to_date (str): End date
            date_column (str): Date column name
            
        Returns:
            str: Modified SQL query with WHERE clause
        """
        where_parts = []
        
        # Add date range condition
        if from_date and to_date and date_column:
            where_parts.append(f"{date_column} BETWEEN '{from_date}' AND '{to_date}'")
        
        # Add other filters
        for column, filter_item in filter_values.items():
            operator = filter_item.get('o', '=').upper()
            value = filter_item.get('v', '')
            
            if operator == 'LIKE':
                value = f"'%{value}%'"
            elif not str(value).replace('.', '').isdigit():
                value = f"'{value}'"
            
            where_parts.append(f"{column} {operator} {value}")
        
        # Remove existing WHERE
        sql = re.sub(r'\s+WHERE\s+.*?(ORDER\s+BY|GROUP\s+BY|LIMIT|$)', r' \1', sql, flags=re.IGNORECASE)
        
        if where_parts:
            sql = re.sub(r'(ORDER\s+BY|GROUP\s+BY|LIMIT|$)', f'WHERE {" AND ".join(where_parts)} \\1', sql, count=1, flags=re.IGNORECASE)
        
        return sql

    @staticmethod
    def add_where_condition(sql, condition):
        """
        Add a WHERE condition to SQL query, handling existing WHERE clauses
        
        Args:
            sql (str): Original SQL query
            condition (str): WHERE condition to add (without WHERE keyword)
            
        Returns:
            str: Modified SQL query with WHERE condition
        """
        if not condition:
            return sql
        
        # Check if WHERE already exists
        if re.search(r'\bWHERE\b', sql, re.IGNORECASE):
            # Add AND condition to existing WHERE
            sql = re.sub(r'(\bWHERE\s+[^)]+?)(\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)', 
                        rf'\1 AND ({condition})\2', sql, flags=re.IGNORECASE)
        else:
            # Add new WHERE clause before ORDER BY, GROUP BY, or LIMIT
            sql = re.sub(r'(\s+)(ORDER\s+BY|GROUP\s+BY|LIMIT|$)', 
                        rf' WHERE ({condition})\1\2', sql, flags=re.IGNORECASE, count=1)
            # If no ORDER BY, GROUP BY, or LIMIT, append at the end
            if not re.search(r'\bWHERE\b', sql, re.IGNORECASE):
                sql = f"{sql.rstrip()} WHERE ({condition})"
        
        return sql

    @staticmethod
    def sanitize_json_data(data):
        """
        Sanitize JSON data by converting None values to empty strings
        
        Args:
            data: JSON data to sanitize
            
        Returns:
            dict/list: Sanitized data
        """
        if isinstance(data, dict):
            return {key: SqlHelperService.sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [SqlHelperService.sanitize_json_data(item) for item in data]
        elif data is None:
            return ""
        else:
            return data 