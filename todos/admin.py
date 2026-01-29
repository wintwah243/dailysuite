from django.contrib import admin

from todos.models import *

# Register your models here.

admin.site.register(Task)
admin.site.register(Option)
admin.site.register(Priority)

