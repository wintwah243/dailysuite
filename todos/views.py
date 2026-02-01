from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *

# Create your views here.
def todo(request):
    tasks = Task.objects.all()
    for task in tasks:
        task.form = TaskForm(instance=task)
    add_form = TaskForm()
    return render(request, 'todos/todohome.html', {'tasks': tasks, 'add_form': add_form})

def addtask(request):
    if request.method == 'POST':
        taskform = TaskForm(request.POST)
        if taskform.is_valid():
            taskform.save()
    return redirect('todolist')


def updatetask(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        taskform = TaskForm(request.POST, instance=task)
        if taskform.is_valid():
            taskform.save()
    return redirect('todolist')

def deletetask(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    return redirect('todolist')

def toggle_task(request, id):
    task = Task.objects.get(id=id)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('todolist')

