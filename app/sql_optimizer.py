# import re

# def optimize_sql_query(query):
#     original = query.strip()

#     # Replace SELECT * with named columns (only for known queries)
#     if re.search(r"select\s+\*", original, re.IGNORECASE):
#         if "from customers" in original.lower():
#             query = re.sub(r"(?i)select\s+\*", "SELECT CustomerID, CompanyName, Country", original)
#         elif "from orders" in original.lower():
#             query = re.sub(r"(?i)select\s+\*", "SELECT OrderID, CustomerID, OrderDate, ShipCountry", original)

#     # Add LIMIT 100 if missing and it's a SELECT query
#     if original.lower().startswith("select") and "limit" not in original.lower():
#         query += " LIMIT 100"

#     return query