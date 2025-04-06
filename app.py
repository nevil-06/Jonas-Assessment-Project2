import streamlit as st
from app.prompt_generator import generate_sql_from_nl
from app.sql_executor import execute_sql, is_safe_query
from app.sql_optimizer import optimize_sql_query
from setup.initialize_db import initialize_database
import difflib, sqlite3

# Initialize DB
initialize_database()

# Load schema prompt
with open("prompts/schema_prompt.txt", "r") as f:
    schema_prompt = f.read()

# Test case bank for evaluation
test_case_bank = {
    "Show all customers from Germany": "SELECT CustomerID, CompanyName, Country FROM Customers WHERE Country = 'Germany';",
    "Retrieve all categories from the catalog": "SELECT CategoryID, CategoryName, Description FROM Categories;",
    "How many orders are there?": "SELECT COUNT(*) FROM Orders;",
    "Which products are discontinued?": "SELECT ProductID, ProductName FROM Products WHERE Discontinued = '1';"
}
def normalize_result(cursor):
    """Normalize results into sorted list of lowercase tuples (order-agnostic)."""
    columns = [desc[0].lower() for desc in cursor.description]
    rows = cursor.fetchall()
    return sorted([tuple(str(cell).strip().lower() for cell in row) for row in rows])


# Evaluation utilities
def similarity_score(pred, target):
    return difflib.SequenceMatcher(None, pred.strip().lower(), target.strip().lower()).ratio()

def compute_precision_recall_f1(pred, target):
    pred_tokens = pred.strip().lower().split()
    target_tokens = target.strip().lower().split()
    pred_set = set(pred_tokens)
    target_set = set(target_tokens)

    tp = len(pred_set & target_set)
    fp = len(pred_set - target_set)
    fn = len(target_set - pred_set)

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)
    return round(precision, 3), round(recall, 3), round(f1, 3)

# UI
st.set_page_config(page_title="Text-to-SQL Demo", layout="centered")
st.title("🧠 Text-to-SQL System")
st.caption("Natural language to SQL conversion using Northwind dataset")

tab1, tab2 = st.tabs(["💬 SQL Query", "📊 Evaluation"])

with tab1:
    st.subheader("🔍 Ask a Question")

    # Dropdown of test cases
    test_question = st.selectbox("Choose a sample question (or enter your own below):", [""] + list(test_case_bank.keys()))
    user_input = st.text_input("Or type your own question:", test_question if test_question else "")

    if user_input:
        sql_query = generate_sql_from_nl(user_input, schema_prompt)
        optimized_sql = optimize_sql_query(sql_query, user_input)

        st.subheader("⚙️ Optimized SQL")
        st.code(optimized_sql, language="sql")

        if not is_safe_query(optimized_sql):
            st.error("❌ Only SELECT queries are allowed.")
        else:
            if st.button("📊 Show Results"):
                result = execute_sql(optimized_sql)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("✅ Query executed successfully!")
                    st.dataframe(result["rows"], use_container_width=True)

with tab2:
    if user_input and user_input in test_case_bank:
        expected_sql = test_case_bank[user_input]
        sim = similarity_score(optimized_sql, expected_sql)
        precision, recall, f1 = compute_precision_recall_f1(optimized_sql, expected_sql)
        exact = optimized_sql.strip().lower() == expected_sql.strip().lower()

        # Execution match
        try:
            conn = sqlite3.connect("data/northwind.db")
            cursor = conn.cursor()

            cursor.execute(expected_sql)
            expected_result = normalize_result(cursor)

            cursor.execute(optimized_sql)
            predicted_result = normalize_result(cursor)

            execution_match = expected_result == predicted_result
            conn.close()
        except Exception as e:
            execution_match = False
            st.warning(f"⚠️ Execution comparison failed: {e}")

        # Display metrics
        st.subheader("📊 Evaluation Metrics")
        st.markdown(f"**Exact Match:** {'✅ YES' if exact else '❌ NO'}")
        st.markdown(f"**Execution Match:** {'✅ YES' if execution_match else '❌ NO'}")
        st.markdown(f"**Similarity Score:** `{sim:.2f}`")
        st.markdown(f"**Precision:** `{precision}`")
        st.markdown(f"**Recall:** `{recall}`")
        st.markdown(f"**F1 Score:** `{f1}`")

        if execution_match:
            st.success("🎯 SQL query returns the correct result — considered correct.")
        elif not exact:
            st.warning("🟡 SQL is not exact and did not return the same result — needs review.")
    else:
        st.info("ℹ️ Evaluation only available for test cases.")
