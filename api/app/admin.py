from django.contrib import admin
from .models import CustomUser, Problem, TestCases,Submissions

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Problem)
admin.site.register(TestCases)
admin.site.register(Submissions)
