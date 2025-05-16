from django.db import models

class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    grade = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    student_id = models.CharField(max_length=8, unique=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)

    def __str__(self):
        return self.name
