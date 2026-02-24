from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

from .models import Course, Subject, Student, Faculty, Attendance, Marks


# ================= LOGIN =================
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


# ================= DASHBOARD =================
@login_required
def dashboard(request):

    # ---------- STUDENT ----------
    if hasattr(request.user, 'student'):
        student = request.user.student

        attendance_records = Attendance.objects.filter(
            student=student
        ).select_related('subject').order_by('-date')

        marks_records = Marks.objects.filter(student=student).select_related('subject')

        total_classes = attendance_records.count()
        present_classes = attendance_records.filter(status=True).count()

        attendance_percentage = 0
        if total_classes > 0:
            attendance_percentage = (present_classes / total_classes) * 100

        marks_percentage = 0
        if marks_records.count() > 0:
            marks_percentage = sum(m.marks for m in marks_records) / marks_records.count()

        return render(request, 'student_dashboard.html', {
            'student': student,
            'attendance_records': attendance_records,
            'attendance_percentage': round(attendance_percentage, 2),
            'marks_percentage': round(marks_percentage, 2),
            'marks_records': marks_records
        })

    # ---------- FACULTY ----------
    elif hasattr(request.user, 'faculty'):
        faculty = request.user.faculty
        subjects = faculty.subjects.all()

        return render(request, 'faculty_dashboard.html', {
            'faculty': faculty,
            'subjects': subjects
        })

    # ---------- ADMIN ----------
    elif request.user.is_superuser:
        return render(request, 'admin_dashboard.html')

    # ---------- UNASSIGNED ----------
    else:
        return render(request, 'unassigned_user.html')


# ================= MARK ATTENDANCE =================
@login_required
def mark_attendance(request):
    faculty = request.user.faculty
    subjects = faculty.subjects.all()

    selected_subject = None
    students = []

    if request.method == "POST":
        subject_id = request.POST.get('subject')
        selected_subject = Subject.objects.get(id=subject_id)

        if selected_subject not in subjects:
            return redirect('dashboard')

        students = Student.objects.filter(course=selected_subject.course)

        # If attendance is being submitted
        if request.POST.get('attendance_date'):
            selected_date = request.POST.get('attendance_date')

            for student in students:
                status = request.POST.get(str(student.id)) == 'on'
                Attendance.objects.create(
                    student=student,
                    subject=selected_subject,
                    date=selected_date,
                    status=status
                )

            return redirect('dashboard')

    return render(request, 'mark_attendance.html', {
        'subjects': subjects,
        'students': students,
        'selected_subject': selected_subject
    })

# ================= ADD MARKS =================
@login_required
def add_marks(request):
    faculty = request.user.faculty
    subjects = faculty.subjects.all()

    selected_subject = None
    students = []

    if request.method == "POST":
        subject_id = request.POST.get('subject')
        selected_subject = Subject.objects.get(id=subject_id)

        # Security check
        if selected_subject not in subjects:
            return redirect('dashboard')

        students = Student.objects.filter(course=selected_subject.course)

        # Save marks only if any mark value is submitted
        marks_entered = any(
            request.POST.get(str(student.id)) for student in students
        )

        if marks_entered:
            for student in students:
                value = request.POST.get(str(student.id))
                if value:
                    Marks.objects.update_or_create(
                        student=student,
                        subject=selected_subject,
                        defaults={'marks': value}
                    )
            return redirect('dashboard')

    return render(request, 'add_marks.html', {
        'subjects': subjects,
        'students': students,
        'selected_subject': selected_subject
    })

# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":
        username = request.POST['username']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=request.POST['email'],
            password=request.POST['password']
        )

        messages.success(request, "Account created. Please login.")
        return redirect('login')

    return render(request, 'register.html')


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('login')