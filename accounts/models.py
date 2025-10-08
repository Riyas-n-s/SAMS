from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.core.validators import MinLengthValidator



  # 👈 Fix: import Student from your app, not django.dispatch


class Student(models.Model):
    
    name = models.CharField(max_length=100)
    register_number = models.CharField(
    max_length=20,
    unique=True,
    validators=[MinLengthValidator(6, message="Register number must be at least 6 characters.")]
    )
    branch = models.CharField(max_length=50)
    semester = models.IntegerField()
    roll_number = models.PositiveIntegerField()
    seen_materials = models.ManyToManyField('StudyMaterial', blank=True, related_name='seen_by')

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Link to login user
   


    def __str__(self):
        return f"{self.name} ({self.register_number})"

    

   
class Staff(models.Model):
    name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.name} ({self.staff_id})"




from django.db import models

class OthersStaff(models.Model):
    staff_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    staff_in_charge = models.CharField(
        max_length=100,
        
        help_text="E.g., Hostel, Library, Sports, etc."
        
    )

    def __str__(self):
        return f"{self.name} ({self.staff_in_charge})"


class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('others', 'Others'),
        ('admin', 'Admin'),
    ]
    student = models.OneToOneField(Student, null=True, blank=True, on_delete=models.CASCADE, related_name='profile_for_student')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    branch = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    register_number = models.CharField(max_length=20, blank=True, null=True)
    staff_id = models.CharField(max_length=20, blank=True, null=True)
    semester = models.IntegerField(null=True, blank=True)
    staff_in_charge = models.CharField(max_length=100, blank=True, null=True, help_text="For Others role: Hostel, Library, Sports, etc.")
    # other fields...
    

    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female')],
        null=True,
        blank=True
    )
    address = models.TextField(blank=True, null=True)

    profile_completed = models.BooleanField(default=False)  # flag




    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def get_dashboard_url(self):
        if self.role == 'student':
            return '/student/'
        elif self.role == 'teacher':
            return '/teacher/'
        elif self.role == 'others':
            return '/others-dashboard/'
        return '/admin-dashboard/'





#teacher


class Subject(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    semester = models.IntegerField()  # <-- Add
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)  # Who added this subject

    code = models.CharField(max_length=20) 
    branch = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Sem {self.semester} ({self.branch})"




from django.db import models
from django.contrib.auth.models import User

class StudyMaterial(models.Model):
    CATEGORY_CHOICES = [
        ('notes', 'Study Notes'),
        ('links', 'Links / Recorded Classes'),
        ('qp', 'Previous Question Papers'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    semester = models.IntegerField()
    file = models.FileField(upload_to='study_materials/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    branch = models.CharField(max_length=50)  # <-- ADD THIS

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"



class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    hour = models.CharField(max_length=10)
    topic = models.TextField(blank=True)
    present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'subject', 'date', 'hour')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.subject.name}"


from django.db import models
from django.contrib.auth.models import User




class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    file = models.FileField(upload_to="assignments/")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignments/submissions/')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('graded', 'Graded')], default='pending')
    marks = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"



#doubts


from django.db import models
from django.contrib.auth.models import User



class Doubt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_doubts")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_doubts")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doubt: {self.student.username} - {self.subject.name}"

class DoubtMessage(models.Model):
    doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='doubt_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_unsent = models.BooleanField(default=False) 

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20] if self.message else 'File'}"




class NoDues(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    has_dues = models.BooleanField(default=True)
    due_date = models.DateField(null=True, blank=True)
    remark = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dues for {self.student} - {self.department} - {'Pending' if self.has_dues else 'Cleared'}"
    


from django.db import models
from django.contrib.auth.models import User

class CGPARecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)
    semester = models.IntegerField()
    sgpa = models.FloatField()
    total_credits = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'department', 'semester')
        ordering = ['semester']

    def __str__(self):
        return f"{self.user.username} - {self.department} - Sem {self.semester}: SGPA {self.sgpa}"
    


    