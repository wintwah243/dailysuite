from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *

# Create your views here.
def todo(request):
    tasks = Task.objects.all()
    return render(request, 'todos/todohome.html', {'tasks': tasks})

def addtask(request):
    if request.method == 'POST':
        taskform = TaskForm(request.POST)
        if taskform.is_valid():
            taskform.save()
            return redirect('todolist')
    else:
        taskform = TaskForm()
    return render(request, 'todos/addtask.html', {'forms': taskform})

def updatetask(request, id):
    task = Task.objects.get(id=id)
    if request.method == 'POST':
        taskform = TaskForm(request.POST, instance=task)
        if taskform.is_valid():
            taskform.save()
            return redirect('todolist')
    else:
        taskform = TaskForm(instance=task)
    return render(request, 'todos/updatetask.html', {'forms': taskform})

def deletetask(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect('todolist')

def toggle_task(request, id):
    task = Task.objects.get(id=id)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('todolist')

