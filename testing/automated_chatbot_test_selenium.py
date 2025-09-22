from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Define the URL of the chatbot frontend
CHATBOT_URL = "http://localhost:3000"

# Define the file containing the questions
QUESTIONS_FILE = "questions.txt"

# Define the output file for results
OUTPUT_FILE = "test_results.csv"

def load_questions(file_path):
    """Load questions from a text file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def test_chatbot(questions):
    """Test the chatbot with a list of questions using Selenium."""
    # Set up the Selenium WebDriver (ensure you have the correct driver installed, e.g., chromedriver)
    service = Service("C:\\Users\\erlan\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(CHATBOT_URL)

    results = []

    try:
        for i, question in enumerate(questions):
            print(f"Testing question {i + 1}/{len(questions)}: {question}")

            # Find the input box and send the question
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            input_box.clear()
            input_box.send_keys(question)
            input_box.send_keys(Keys.RETURN)

            # Wait for the response to appear
            start_time = time.time()
            try:
                response_element = WebDriverWait(driver, 15).until(  # Reduced wait time to 15 seconds
                    EC.presence_of_element_located((By.CLASS_NAME, "response"))  # Adjust class name as needed
                )
                response_time = time.time() - start_time
                response_text = response_element.text

                results.append({
                    "question": question,
                    "response": response_text,
                    "response_time": response_time,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "question": question,
                    "response": "",
                    "response_time": None,
                    "status": f"timeout or error: {str(e)}"
                })

            save_results(results, OUTPUT_FILE)  # Save results after each question

    finally:
        driver.quit()

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
