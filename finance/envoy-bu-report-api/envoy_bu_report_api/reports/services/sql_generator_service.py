import json
import psycopg2
from django.conf import settings


class SQLGeneratorService:
    @staticmethod
    def generate_from_input(json_input):
        """
        Generate SQL query from JSON input configuration
        
        Args:
            json_input (str or dict): JSON configuration with fields and filters
            
        Returns:
            str: Generated SQL query
        """
        try:
            # Parse JSON input
            data = json.loads(json_input) if isinstance(json_input, str) else json_input
            
            fields = data.get('fields', [])
            filters = data.get('filters', [])
            
            if not fields:
                return "Invalid input: 'fields' missing or not an array."
            
            # Build SELECT clause
            select_parts = []
            aliases_used = {}
            
            for field in fields:
                if not all(key in field for key in ['code', 'label']):
                    continue
                    
                parts = field['code'].split('.')
                if len(parts) != 2:
                    continue
                    
                alias, column = parts
                aliases_used[alias] = True
                select_parts.append(f"{alias}.{column} AS \"{field['label']}\"")
            
            if not aliases_used:
                return "No valid aliases found in fields."
            
            # Build FROM clause (use first alias as base)
            base_alias = list(aliases_used.keys())[0]
            
            # Build SQL
            sql = f"SELECT\n  {',\n  '.join(select_parts)}\n"
            sql += f"FROM {base_alias}\n"
            
            # Add WHERE clause if filters exist
            where_clauses = []
            for filter_item in filters:
                if filter_item.get('code') and filter_item.get('default'):
                    where_clauses.append(f"{filter_item['code']} = '{filter_item['default']}'")
            
            if where_clauses:
                sql += f"WHERE {' AND '.join(where_clauses)}\n"
            
            sql += ";"
            return sql
            
        except Exception as e:
            return f"Error generating SQL: {str(e)}" 