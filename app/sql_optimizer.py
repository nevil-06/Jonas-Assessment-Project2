# sql_optimizer.py

import re

def optimize_sql_query(query, original_question=None):
    # Normalize and strip any trailing semicolon
    query = query.strip().rstrip(';')

    # Replace SELECT * with specific column selections
    if re.search(r"select\s+\*", query, re.IGNORECASE):
        if "from customers" in query.lower():
            query = re.sub(r"(?i)select\s+\*", "SELECT CustomerID, CompanyName, Country", query)
        elif "from orders" in query.lower():
            query = re.sub(r"(?i)select\s+\*", "SELECT OrderID, CustomerID, OrderDate, ShipCountry", query)
        elif "from products" in query.lower():
            query = re.sub(r"(?i)select\s+\*", "SELECT ProductID, ProductName, UnitPrice", query)
        elif "from categories" in query.lower():
            query = re.sub(r"(?i)select\s+\*", "SELECT CategoryID, CategoryName", query)
        elif "from order details" in query.lower():
            query = re.sub(r"(?i)select\s+\*", "SELECT OrderID, ProductID, Quantity, UnitPrice", query)

    # Append LIMIT 100 if not already present and not explicitly asking for all
    if (
        query.lower().startswith("select") and
        "limit" not in query.lower() and
        (not original_question or "all" not in original_question.lower())
    ):
        query += " LIMIT 100"

    # Always return with a single semicolon at the end
    return query.strip() + ';'