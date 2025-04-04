import json
import difflib
from app.prompt_generator import generate_sql_from_nl
# from app.sql_optimizer import optimize_sql_query

# Load test cases (expected format: [{"question": ..., "expected_sql": ...}])
with open("tests/test_cases.json", "r") as f:
    test_cases = json.load(f)

# Load prompt template
with open("prompts/schema_prompt.txt", "r") as f:
    schema_prompt = f.read()


def is_exact_match(predicted, target):
    return predicted.strip().lower() == target.strip().lower()


def similarity_score(predicted, target):
    return difflib.SequenceMatcher(None, predicted.strip().lower(), target.strip().lower()).ratio()


def compute_precision_recall_f1(predicted, target):
    pred_tokens = predicted.strip().lower().split()
    target_tokens = target.strip().lower().split()

    pred_set = set(pred_tokens)
    target_set = set(target_tokens)

    true_positive = len(pred_set & target_set)
    false_positive = len(pred_set - target_set)
    false_negative = len(target_set - pred_set)

    precision = true_positive / (true_positive + false_positive + 1e-8)
    recall = true_positive / (true_positive + false_negative + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)

    return round(precision, 3), round(recall, 3), round(f1, 3)


def run_evaluation():
    exact_matches = 0
    precision_total = recall_total = f1_total = 0
    total = len(test_cases)

    print("\n📊 Evaluation Results\n" + "-" * 40)

    for i, case in enumerate(test_cases):
        question = case["question"]
        expected_sql = case["expected_sql"]

        predicted_sql = generate_sql_from_nl(question, schema_prompt)
        # predicted_sql = optimize_sql_query(predicted_sql)

        print(f"Test {i+1}: {question}")
        print("Expected:", expected_sql)
        print("Predicted:", predicted_sql)

        if is_exact_match(predicted_sql, expected_sql):
            exact_matches += 1
            print("✅ Exact Match")
        else:
            print("❌ Not an Exact Match")

        sim = similarity_score(predicted_sql, expected_sql)
        precision, recall, f1 = compute_precision_recall_f1(predicted_sql, expected_sql)

        print(f"🔍 Similarity: {sim:.2f} | Precision: {precision} | Recall: {recall} | F1: {f1}")
        print("-" * 40)

        precision_total += precision
        recall_total += recall
        f1_total += f1

    # Summary
    print("\n✅ Evaluation Summary")
    print(f"Exact Match Accuracy: {exact_matches}/{total} = {exact_matches / total:.2f}")
    print(f"Avg Precision: {precision_total / total:.3f}")
    print(f"Avg Recall:    {recall_total / total:.3f}")
    print(f"Avg F1-Score:  {f1_total / total:.3f}")


if __name__ == "__main__":
    run_evaluation()