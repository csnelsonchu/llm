import pandas as pd
from pandasql import sqldf
import requests
import json
import os

inference_url = os.getenv("INFERENCE_URL") 
def load_employee_df():
    file_path = 'data/employee.csv'
    employee = pd.read_csv(file_path)
    return employee

def get_prompt_sql(question):
    file_path = 'data/prompt.sql.template'
    file_content = None
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content.format(question=question), ["```"]

def get_prompt_result(question, results):
    file_path = 'data/prompt.result.template'
    file_content = None
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content.format(question=question, results=results), []

def inference(prompt, stop_sequences):
    payload = json.dumps({
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 100,
        "temperature": 0.2,
        "top_p": 0.2,
        "stop_sequences": stop_sequences,
    }
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", inference_url, headers=headers, data=payload)
    text = response.json()["generated_text"].split("```")[0]
    return text

def query(question):
    prompt_query, stop_sequences = get_prompt_sql(question)
    results_query = inference(prompt=prompt_query,stop_sequences=stop_sequences)
    employee = load_employee_df()
    results_data = sqldf(results_query, locals())
    prompt_answer, stop_sequences = get_prompt_result(question=question, results=results_data)
    answer = inference(prompt=prompt_answer, stop_sequences=stop_sequences)
    return answer

def main():
    while True:
        user_input = input("Ask question about the employee dataset (type 'exit' to stop): ")
        if user_input.lower() == 'exit':
            print("Exiting the loop.")
            break
        answer = query(question=user_input)
        print("************************************************************************************************************************")
        print(answer)
        print("************************************************************************************************************************")
if __name__ == "__main__":
    main()