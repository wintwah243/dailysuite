from django.shortcuts import render, redirect
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



