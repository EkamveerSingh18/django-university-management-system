from django.contrib import admin
from .models import Course, Subject, Student, Faculty, Attendance, Marks

admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Attendance)
admin.site.register(Marks)