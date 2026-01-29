from django.shortcuts import render, redirect

from .forms import TaskForm


# Create your views here.
def todo(request):
    return render(request, 'todos/todohome.html')

def addtask(request):
    if request.method == 'POST':
        taskform = TaskForm(request.POST)
        if taskform.is_valid():
            taskform.save()
            return redirect('todolist')
    else:
        taskform = TaskForm()
    return render(request, 'todos/addtask.html', {'forms': taskform})

