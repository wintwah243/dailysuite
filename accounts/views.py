import requests
import traceback
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def Landing(request):
    return render(request, 'Landing.html')

def home(request):
    return render(request, 'homepage.html')

def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()
        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')


def ai_chat_groq(request):
    print("POST hit:", request.path, request.method)
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    user_message = request.POST.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "Message is required"}, status=400)

    try:
        GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", None)
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in settings.py")

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are DailySuite Assistant, a friendly and helpful customer service chatbot. "
                        "DailySuite is a free productivity app that helps users manage tasks, track budgets, "
                        "take notes, and organize their calendar."
                        "if the user needs further help: wahwint72@gmail.com, +95 9254229977."
                    )
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            "max_completion_tokens": 500
        }

        print("Sending request to Groq API...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print("Groq response status:", response.status_code)
        response.raise_for_status()
        resp_json = response.json()
        print("Groq response JSON:", resp_json)

        # Extract reply from choices
        ai_reply = None
        choices = resp_json.get("choices")
        if isinstance(choices, list) and len(choices) > 0:
            ai_reply = choices[0].get("message", {}).get("content")

        if not ai_reply:
            ai_reply = "AI returned no response."

        return JsonResponse({"reply": ai_reply})

    except requests.exceptions.RequestException as e:
        print("RequestException:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": f"AI API request failed: {str(e)}"}, status=500)

    except Exception as e:
        print("Exception:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
