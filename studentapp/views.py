from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import StudentForm, SignUpForm
from .models import Student
import csv
from django.http import HttpResponse
from django.contrib import messages
import openpyxl # type: ignore
from django.core.paginator import Paginator
from django.db.models import Q

def signup_view(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'studentapp/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_list')  # Redirect to the student list page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'studentapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_list(request):
    students = Student.objects.all()
    print(students)  # Debug: Print the queryset to verify data

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Filter by gender
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        students = students.filter(gender=gender_filter)

    # Filter by grade
    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        students = students.filter(grade=grade_filter)

    # Pagination
    paginator = Paginator(students, 3)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'studentapp/student_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'gender_filter': gender_filter,
        'grade_filter': grade_filter,
    })

@login_required
def register_student(request):
    form = StudentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('student_list')
    return render(request, 'studentapp/register_student.html', {'form': form})

@login_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if form.is_valid():
        form.save()
        return redirect('student_list')
    return render(request, 'studentapp/register_student.html', {'form': form})

@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student_list')

@login_required
def export_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'DOB', 'Gender', 'Grade', 'Address', 'Phone', 'Email', 'Student ID'])

    students = Student.objects.all()
    if not students.exists():
        messages.error(request, "No students available to export.")
        return redirect('student_list')

    for student in students:
        writer.writerow([student.name, student.date_of_birth, student.gender, student.grade,
                         student.address, student.phone, student.email, student.student_id])
    return response

@login_required
def export_excel(request):
    # Create a new workbook and set the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students"

    # Add headers to the worksheet
    headers = ['ID', 'Name', 'Email', 'DOB', 'Gender', 'Grade', 'Address', 'Phone', 'Student ID']
    ws.append(headers)

    # Fetch all students from the database
    students = Student.objects.all()

    # Check if there are any students to export
    if not students.exists():
        messages.error(request, "No students available to export.")
        return redirect('student_list')

    # Add student data to the worksheet
    for student in students:
        ws.append([
            student.id,
            student.name,
            student.email,
            student.date_of_birth,
            student.gender,
            student.grade,
            student.address,
            student.phone,
            student.student_id
        ])

    # Prepare the HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=students.xlsx'

    # Save the workbook to the response
    wb.save(response)
    return response
