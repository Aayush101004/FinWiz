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
    # Handle simple string responses that might not be JSON
    if '"' not in text:
        return json.dumps({"text": text}) # Wrap in a simple JSON
    return ""


async def get_ai_categorization(description: str) -> dict:
    """
    Uses the Gemini API to categorize a single transaction description.
    Returns a dict with keys: category, confidence.
    """
    prompt = f"""
    You are an expert financial assistant. Categorize the following transaction description into one of these categories: {', '.join(CATEGORIES)}.
    Description: '{description}'
    Respond with a JSON object: {{"category": <category>, "confidence": <confidence_score between 0 and 1>}}
    """
    try:
        response = await model.generate_content_async(prompt)
        cleaned = clean_json_response(response.text)
        result = json.loads(cleaned)
        return result
    except Exception as e:
        print(f"Error in get_ai_categorization: {e}")
        return {"category": "Miscellaneous", "confidence": 0.0}

async def get_financial_advice_from_ai(transactions: List[Transaction], prompt: str) -> str:
    """
    Uses the Gemini API to generate financial advice based on transactions and a prompt.
    """
    transaction_list_str = "\n".join([f"- {t.date}: {t.description} (${t.amount:.2f}) -> {t.category}" for t in transactions])

    # --- UPDATED SYSTEM PROMPT ---
    system_prompt = f"""
    You are "FinWiz", a friendly, expert, and insightful AI financial advisor.
    Your tone should be encouraging, clear, and professional. Avoid jargon.
    You will be given a list of a user's recent financial transactions and a specific question or prompt from them.
    **Always refer to currency using the Indian Rupee symbol (₹) instead of the dollar sign ($).**
    
    Your task is to analyze the provided transactions to answer the user's prompt in detail.
    - If they ask for a summary, provide one.
    - If they ask for spending in a category, calculate it.
    - If they ask for "next week's" or "next month's" expenses, you **must** analyze their recurring transactions (like Subscriptions, Utilities, Housing) and spending habits (like Groceries, Transport) to provide a reasonable **forecast** or **prediction**. State your assumptions.
    - If they ask a general question, provide actionable insights.
    
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