from django import forms
from .models import Student
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class StudentForm(forms.ModelForm):
    class Meta: 
        model = Student
        fields = '__all__'

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if not student_id.startswith('CIPL') or len(student_id) != 8:
            raise forms.ValidationError("ID must start with 'CIPL' and be 8 characters.")
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Student ID must be unique.")
        return student_id

class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email
