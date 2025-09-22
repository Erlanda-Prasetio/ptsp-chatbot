import requests
import time
import csv

# Define the URL of the chatbot frontend
CHATBOT_URL = "http://localhost:3000/api/chat"

# Define the file containing the questions
QUESTIONS_FILE = "questions.txt"

# Define the output file for results
OUTPUT_FILE = "test_results.csv"

def load_questions(file_path):
    """Load questions from a text file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def test_chatbot(questions):
    """Test the chatbot with a list of questions."""
    results = []

    for i, question in enumerate(questions):
        print(f"Testing question {i + 1}/{len(questions)}: {question}")
        start_time = time.time()

        try:
            response = requests.post(CHATBOT_URL, json={"message": question})
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                results.append({
                    "question": question,
                    "response": data.get("response", ""),
                    "response_time": response_time,
                    "status": "success"
                })
            else:
                results.append({
                    "question": question,
                    "response": "",
                    "response_time": response_time,
                    "status": f"error {response.status_code}"
                })
        except Exception as e:
            results.append({
                "question": question,
                "response": "",
                "response_time": None,
                "status": f"exception {str(e)}"
            })

    return results

def save_results(results, file_path):
    """Save test results to a CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["question", "response", "response_time", "status"])
        writer.writeheader()
        writer.writerows(results)

def main():
    questions = load_questions(QUESTIONS_FILE)
    results = test_chatbot(questions)
    save_results(results, OUTPUT_FILE)
    print(f"Testing completed. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
