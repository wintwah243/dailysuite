from django.urls import path
from . import views

urlpatterns = [
    path("ai-chat/", views.ai_chat_groq, name="ai_chat"),
]