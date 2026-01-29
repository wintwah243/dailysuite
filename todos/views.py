from django.shortcuts import render

# Create your views here.
def todo(request):
    return render(request, 'todos/todohome.html')
