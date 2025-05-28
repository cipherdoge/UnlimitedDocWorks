import requests
import pandas as pd
from langchain.prompts import PromptTemplate

# Set your Claude 3.5 Sonnet API Key
CLAUDE_API_KEY = "syn-d4fc12c6-7d45-4241-830c-02d30d373c68"

# Correct Claude API endpoint (remove `/Authentication`)
CLAUDE_API_URL = "https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/"

def query_claude(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "api_key": "syn-09df94e0-99be-4056-a7cc-53e30a9a00f2",
        "prompt": prompt,
        "model_id": "claude-3.5-sonnet",
        "model_params": {
            "max_tokens": 512,
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(CLAUDE_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        return response_data.get("response", {}).get("content", [{}])[0].get("text", "").strip()
    
    except requests.exceptions.RequestException as e:
        return f"Error querying Claude: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# Load and clean the dataset
df = pd.read_csv("archive/DataCoSupplyChainDataset.csv", encoding="windows-1252")
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

df['order_date_(dateorders)'] = pd.to_datetime(df['order_date_(dateorders)'], errors='coerce')
df['shipping_date_(dateorders)'] = pd.to_datetime(df['shipping_date_(dateorders)'], errors='coerce')

# Convert duration columns to numeric (integer)
df['days_for_shipping_(real)'] = pd.to_numeric(df['days_for_shipping_(real)'], errors='coerce')
df['days_for_shipment_(scheduled)'] = pd.to_numeric(df['days_for_shipment_(scheduled)'], errors='coerce')

# Function to build query and interpret response via Claude
def lookup_order_stats_with_claude(query: str):
    """
    Use Claude to interpret a question and generate insight based on order data.
    """
    query = query.lower()

    prompt = """
    You are an advanced data analyst assistant. 
    Given a user's question and the dataset's column names, generate a valid **pandas expression** 
    or **Python code snippet** that answers the question using a DataFrame called `df`.

    Only return the Python code needed to compute the result — no explanations, no text, no comments.

    Columns available in the dataset:
    {columns}

    Question: {query}

    Python code:
    """


    prompt_template = PromptTemplate(input_variables=["columns", "query"], template=prompt)

    try:
        full_prompt = prompt_template.format(columns=", ".join(df.columns), query=query)
        nlu_response = query_claude(full_prompt)
        print(nlu_response)
        result = eval(nlu_response)
        return result

    except Exception as e:
        return f"Error processing the query: {str(e)}"
