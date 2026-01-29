from django.urls import path
from . import views

urlpatterns = [
    path('todolist/', views.todo, name='todolist'),
    path('addtask/', views.addtask, name='addtask'),
]