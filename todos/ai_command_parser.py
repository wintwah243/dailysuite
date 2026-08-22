import json
import re
import requests
from django.conf import settings


def parse_todo_command(user_message, username):
    GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", None)
    if not GROQ_API_KEY:
        return {"action": "unknown", "message": "AI assistant not configured"}

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = """You are a task management AI assistant for DailySuite. 
Your job is to parse user commands and return JSON with the following structure:

{
    "action": "delete" or "complete" or "uncomplete" or "add" or "list" or "clear_completed" or "unknown",
    "task_identifier": "task name or ID number (for delete/complete/uncomplete)",
    "task_name": "name of task (for add action)",
    "status": "pending/completed/overdue (for list action)",
    "priority": "low/medium/high (optional for add/list)",
    "option": "option1-option6 (optional for add/list)",
    "due_date": "natural language date like 'tomorrow' or 'next week' (optional for add)",
    "message": "original command or error message"
}

Rules:
- For delete: extract what task to delete (name or ID)
- For complete/uncomplete: extract what task to mark done/undone
- For add: extract task name, optional due date, optional priority, optional option
- For list: extract filters like status, priority, option
- If command is "clear completed", use action "clear_completed"
- If command is ambiguous or not understood, use action "unknown"
- Return ONLY the JSON object, no other text

Examples:
"delete buy milk" -> {"action": "delete", "task_identifier": "buy milk"}
"complete task 5" -> {"action": "complete", "task_identifier": "5"}
"add finish report tomorrow high priority" -> {"action": "add", "task_name": "finish report", "due_date": "tomorrow", "priority": "high"}
"show pending tasks" -> {"action": "list", "status": "pending"}
"clear completed tasks" -> {"action": "clear_completed"}
"""

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.1,
        "max_tokens": 300,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

        # Print raw response text on HTTP errors to catch API issues
        if response.status_code != 200:
            print("Groq API Error Response:", response.text)
            return {"action": "unknown", "message": "AI service returned an error"}

        resp_json = response.json()
        ai_response = resp_json["choices"][0]["message"]["content"]

        # Parse JSON response
        try:
            command_data = json.loads(ai_response)
            if "action" not in command_data:
                command_data["action"] = "unknown"
            return command_data
        except json.JSONDecodeError:
            action_match = re.search(r'"action":\s*"([^"]+)"', ai_response)
            if action_match:
                return {
                    "action": action_match.group(1),
                    "original": user_message,
                }
            return {"action": "unknown", "message": "Could not parse command"}

    except requests.exceptions.RequestException as e:
        print(f"Groq API connection error: {e}")
        return {"action": "unknown", "message": "AI service unavailable"}