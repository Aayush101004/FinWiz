# Add a function to categorize a single transaction description
async def get_ai_categorization(description: str) -> dict:
    """
    Uses the Gemini API to categorize a single transaction description.
    Returns a dict with keys: category, confidence.
    """
    categories = [
        "Groceries", "Restaurants", "Utilities", "Transport", "Shopping",
        "Health", "Entertainment", "Income", "Housing", "Education",
        "Subscriptions", "Travel", "Miscellaneous"
    ]
    prompt = f"""
    You are an expert financial assistant. Categorize the following transaction description into one of these categories: {', '.join(categories)}.
    Description: '{description}'
    Respond with a JSON object: {{"category": <category>, "confidence": <confidence_score between 0 and 1>}}
    """
    response = await model.generate_content_async(prompt)
    cleaned = clean_json_response(response.text)
    result = json.loads(cleaned)
    return result

# Add a function to get AI-powered financial advice
async def get_ai_financial_advice(transactions, prompt: str) -> str:
    """
    Uses the Gemini API to generate financial advice based on transactions and a prompt.
    """
    # transactions is a list of TransactionResponse
    transaction_list_str = "\n".join([
        f"- {t.date}: {t.description} (${t.amount:.2f}) -> {t.category}" for t in transactions
    ])
    system_prompt = f"""
    You are 'FinWiz', a friendly and insightful AI financial advisor.
    Your tone should be encouraging, clear, and helpful. Avoid jargon.
    You will be given a list of a user's recent financial transactions and a specific question or prompt from them.
    Analyze the provided transactions to answer the user's prompt. Provide actionable insights and summaries.
    Be concise but thorough. Use markdown for formatting (like lists or bold text) to improve readability.

    Here are the user's transactions:
    {transaction_list_str}
    """
    full_prompt = f"{system_prompt}\n\nUser's request: {prompt}"
    response = await model.generate_content_async(full_prompt)
    return response.text
import json
import os
import re
from typing import Dict, List

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# Define a list of standard categories for consistency
CATEGORIES = [
    "Groceries", "Restaurants", "Utilities", "Transport", "Shopping",
    "Health", "Entertainment", "Income", "Housing", "Education",
    "Subscriptions", "Travel", "Miscellaneous"
]

class Transaction(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    category: str

def clean_json_response(text: str) -> str:
    """Cleans the raw text response from Gemini to extract a valid JSON string."""
    # Find the start and end of the JSON block
    json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    # Fallback for cases where the markers are missing but content is JSON-like
    if text.strip().startswith('{') or text.strip().startswith('['):
        return text.strip()
    return ""


async def get_transaction_categories(descriptions: List[str]) -> List[Dict[str, str]]:
    """
    Uses the Gemini API to categorize a list of transaction descriptions.
    """
    prompt = f"""
    You are an expert financial assistant. Your task is to categorize a list of bank transaction descriptions.
    For each description, assign it one of the following categories: {", ".join(CATEGORIES)}.
    If a category is not obvious, use 'Miscellaneous'.

    Analyze the following list of transaction descriptions:
    {descriptions}

    Return your response as a single JSON array of objects. Each object should have two keys: "description" and "category".
    For example: `[ {{"description": "AMAZON.COM", "category": "Shopping"}}, {{"description": "UBER EATS", "category": "Restaurants"}} ]`
    Do not include any text outside of the JSON array.
    """
    try:
        response = await model.generate_content_async(prompt)
        cleaned_response = clean_json_response(response.text)

        if not cleaned_response:
             raise ValueError("AI response did not contain a valid JSON block.")

        categorized_list = json.loads(cleaned_response)

        # Ensure the response is a list of dicts with the correct keys
        if not isinstance(categorized_list, list) or not all(isinstance(item, dict) and 'description' in item and 'category' in item for item in categorized_list):
            raise ValueError("Parsed JSON from AI is not in the expected format.")

        return categorized_list
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from Gemini response.")
        print(f"Raw response was: {response.text}")
        raise ValueError("AI response was not valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred in get_transaction_categories: {e}")
        raise

async def get_financial_advice_from_ai(transactions: List[Transaction], prompt: str) -> str:
    """
    Uses the Gemini API to generate financial advice based on transactions and a prompt.
    """
    transaction_list_str = "\n".join([f"- {t.date}: {t.description} (${t.amount:.2f}) -> {t.category}" for t in transactions])

    system_prompt = f"""
    You are "FinWiz", a friendly and insightful AI financial advisor.
    Your tone should be encouraging, clear, and helpful. Avoid jargon.
    You will be given a list of a user's recent financial transactions and a specific question or prompt from them.
    Analyze the provided transactions to answer the user's prompt. Provide actionable insights and summaries.
    Be concise but thorough. Use markdown for formatting (like lists or bold text) to improve readability.

    Here are the user's transactions:
    {transaction_list_str}
    """

    full_prompt = f"{system_prompt}\n\nUser's request: {prompt}"

    try:
        response = await model.generate_content_async(full_prompt)
        return response.text
    except Exception as e:
        print(f"An unexpected error occurred in get_financial_advice_from_ai: {e}")
        return "I'm sorry, I encountered an issue while generating advice. Please try again."