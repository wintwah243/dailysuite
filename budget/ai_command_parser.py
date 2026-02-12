import requests
import json
from django.conf import settings


def parse_budget_command(user_message, username):
    GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", None)
    if not GROQ_API_KEY:
        return {
            "action": "unknown",
            "message": "AI assistant not configured"
        }

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = """You are a budget management AI assistant for DailySuite.
Your job is to parse user commands about income, expenses, and budgets into structured JSON.

Return ONLY a JSON object with this structure:
{
    "action": "add_income" or "add_expense" or "delete_income" or "delete_expense" or "delete_last" or "summary" or "category_spending" or "list" or "unknown",
    "amount": "numeric amount (for add commands)",
    "source": "income source name (for add_income)",
    "description": "expense description (for add_expense)",
    "category": "category name (for add_expense or category_spending)",
    "identifier": "ID or name to delete (for delete_commands)",
    "transaction_type": "income/expense (for delete_last or list)",
    "period": "today/week/month/year (for summary)",
    "limit": "number of transactions (for list)"
}

Examples:
"add income 3000 salary today" -> {"action": "add_income", "amount": "3000", "source": "salary", "date": "today"}
"add expense 25.50 for lunch food" -> {"action": "add_expense", "amount": "25.50", "description": "lunch", "category": "food"}
"delete income 5" -> {"action": "delete_income", "identifier": "5"}
"delete last expense" -> {"action": "delete_last", "transaction_type": "expense"}
"show my budget summary" -> {"action": "summary"}
"how much did I spend on food" -> {"action": "category_spending", "category": "food"}
"show my expenses" -> {"action": "list", "transaction_type": "expense", "limit": "5"}
"show all transactions" -> {"action": "list", "limit": "10"}

If you don't understand, return {"action": "unknown"}.
"""

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "max_tokens": 300,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        resp_json = response.json()

        ai_response = resp_json["choices"][0]["message"]["content"]

        try:
            command_data = json.loads(ai_response)
            if "action" not in command_data:
                command_data["action"] = "unknown"
            return command_data
        except json.JSONDecodeError:
            return {"action": "unknown", "original": user_message}

    except Exception as e:
        print(f"Groq API error: {e}")
        return {"action": "unknown", "message": "AI service unavailable"}