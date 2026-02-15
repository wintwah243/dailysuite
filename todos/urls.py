from django.urls import path
from . import views
from . import views_chat

urlpatterns = [
    path('todolist/', views.todo, name='todolist'),
    path('addtask/', views.addtask, name='addtask'),
    path('updatetask/<int:id>', views.updatetask, name='updatetask'),
    path('deletetask/<int:id>', views.deletetask, name='deletetask'),
    path('toggle/<int:id>/', views.toggle_task, name='toggle_task'),

    path('api/chat-command/', views_chat.todo_chat_command, name='todo_chat_command'),
    path('api/tasks-json/', views_chat.get_tasks_json, name='tasks_json'),

    path('toggle-pin/<int:task_id>/', views.toggle_pin, name='toggle_pin'),
]