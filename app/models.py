from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.IntegerField()

    def __str__(self):
        return self.user.username


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject)

    def __str__(self):
        return self.user.username


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField()

    def __str__(self):
        return f"{self.student} - {self.subject}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student} - {self.subject}"