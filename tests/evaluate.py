import pandas as pd
import json
import difflib
import sqlite3
from app.prompt_generator import generate_sql_from_nl
from app.sql_optimizer import optimize_sql_query

# --- Load test cases ---
with open("tests/test_cases.json", "r") as f:
    test_cases = json.load(f)

# --- Load schema prompt ---
with open("prompts/schema_prompt.txt", "r") as f:
    schema_prompt = f.read()

# --- Connect to DB ---
conn = sqlite3.connect("data/northwind.db")
cursor = conn.cursor()

# --- Utility functions ---
def normalize_result(rows):
    return sorted([tuple(str(cell).strip().lower() for cell in row) for row in rows])

def similarity_score(predicted, target):
    return difflib.SequenceMatcher(None, predicted.strip().lower(), target.strip().lower()).ratio()

def compute_precision_recall_f1(predicted, target):
    pred_tokens = predicted.strip().lower().split()
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

# --- Evaluation Loop ---
results = []
exact_matches = 0
execution_matches = 0
precision_total = recall_total = f1_total = sim_total = 0

for idx, case in enumerate(test_cases, 1):
    question = case["question"]
    expected_sql = case["expected_sql"]

    # Step 1: Generate + optimize SQL
    predicted_sql = generate_sql_from_nl(question, schema_prompt)
    optimized_sql = optimize_sql_query(predicted_sql, question)

    # Step 2: Execution-based comparison
    try:
        cursor.execute(expected_sql)
        expected_result = normalize_result(cursor.fetchall())
    except Exception as e:
        expected_result = f"Error: {e}"

    try:
        cursor.execute(optimized_sql)
        predicted_result = normalize_result(cursor.fetchall())
    except Exception as e:
        predicted_result = f"Error: {e}"

    # Step 3: Metrics
    is_exact = expected_sql.strip().lower() == optimized_sql.strip().lower()
    sim = similarity_score(expected_sql, optimized_sql)
    precision, recall, f1 = compute_precision_recall_f1(expected_sql, optimized_sql)
    exec_match = expected_result == predicted_result

    if is_exact:
        exact_matches += 1
    if exec_match:
        execution_matches += 1

    precision_total += precision
    recall_total += recall
    f1_total += f1
    sim_total += sim

    results.append({
        "Test #": idx,
        "Question": question,
        "Expected SQL": expected_sql,
        "Predicted SQL": optimized_sql,
        "Exact Match": is_exact,
        "Execution Match": exec_match,
        "Similarity": round(sim, 2),
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    })

conn.close()

# --- Convert to DataFrame and show summary ---
df = pd.DataFrame(results)
total = len(df)

print("\n📊 Evaluation Summary")
print("-" * 40)
print(f"Total test cases:      {total}")
print(f"Exact SQL matches:     {exact_matches} ({exact_matches / total:.2%})")
print(f"Execution matches:     {execution_matches} ({execution_matches / total:.2%})")
print(f"Avg Precision:         {precision_total / total:.3f}")
print(f"Avg Recall:            {recall_total / total:.3f}")
print(f"Avg F1 Score:          {f1_total / total:.3f}")
print(f"Avg SQL Similarity:    {sim_total / total:.2f}")
print("-" * 40)

# Optional: save results
# df.to_csv("evaluation_results.csv", index=False)


for i, case in enumerate(test_cases, 1):
    question = case["question"]
    expected_sql = case["expected_sql"]

    predicted_sql = generate_sql_from_nl(question, schema_prompt)
    optimized_sql = optimize_sql_query(predicted_sql, question)

    is_exact = expected_sql.strip().lower() == optimized_sql.strip().lower()

    print(f"\n🧪 Test Case {i}")
    print(f"🔹 Question        : {question}")
    print(f"🔸 Expected SQL    : {expected_sql}")
    print(f"🔸 Predicted SQL   : {optimized_sql}")
    print(f"✅ Exact Match     : {'✅ YES' if is_exact else '❌ NO'}")
    print("-" * 60)
