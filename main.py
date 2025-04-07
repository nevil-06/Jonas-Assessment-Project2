from app.prompt_generator import generate_sql_from_nl
from app.sql_executor import execute_sql, is_safe_query
from setup.initialize_db import initialize_database
from dotenv import load_dotenv
from app.sql_optimizer import optimize_sql_query

# Load env variables
load_dotenv()

# Initialize the database (runs once)
initialize_database()

# Load schema prompt
with open("prompts/schema_prompt.txt", "r") as f:
    schema_info = f.read()

print("💬 Text-to-SQL System is ready!\n")

# Run main loop
while True:
    user_input = input("Ask a question (or type 'exit'): ")
    if user_input.strip().lower() == "exit":
        print("👋 Goodbye!")
        break

    sql_query = generate_sql_from_nl(user_input, schema_info)
    optimized_query = optimize_sql_query(sql_query, user_input)
    if not is_safe_query(optimized_query):
        print("🚫 Only SELECT queries are allowed. Please rephrase.")
        continue
    print("\n🧠 Generated SQL:\n", sql_query)
    print("⚡ Optimized SQL:\n", optimized_query)
