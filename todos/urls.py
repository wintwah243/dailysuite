from django.urls import path
from . import views

urlpatterns = [
    path('todolist/', views.todo, name='todolist'),
    path('addtask/', views.addtask, name='addtask'),
    path('updatetask/<int:id>', views.updatetask, name='updatetask'),
    path('deletetask/<int:id>', views.deletetask, name='deletetask'),
    path('toggle/<int:id>/', views.toggle_task, name='toggle_task'),

]