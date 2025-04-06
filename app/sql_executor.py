# sql_executor.py
import sqlite3
import sqlparse

def is_safe_query(query):
    try:
        parsed = sqlparse.parse(query)
        return all(stmt.get_type() == 'SELECT' for stmt in parsed)
    except Exception:
        return False

def execute_sql(query, db_path="data/northwind.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        return {"columns": columns, "rows": rows}
    except sqlite3.OperationalError as e:
        return {"error": f"⚠️ SQL Error: {str(e)}. Please check column or table names."}
    except Exception as e:
        return {"error": f"⚠️ Unexpected error: {str(e)}. Try rephrasing your question."}
