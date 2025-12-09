from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Attendance, Student, Profile

from django.contrib.auth.decorators import login_required
from datetime import date

from accounts.students.forms import ProfileCompletionForm
@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == "student" and not profile.profile_completed:
        return redirect('complete_profile')
    student = Student.objects.get(register_number=profile.register_number)
    return render(request, 'students/dashboard.html', {'student': student})

@login_required
def profile(request):
    profile = request.user.profile
    return render(request, "students/profile.html", {"profile": profile})


# views.py
@login_required
def complete_profile(request):
    profile = request.user.profile

    if profile.profile_completed:
        return redirect(profile.get_dashboard_url())
    
        # Prefill email and branch if not already filled
    if not profile.email:
        profile.email = profile.user.email  # get email from User model
    if not profile.branch:
        profile.branch = profile.branch or ''  # optional, if you have default branch



    if request.method == "POST":
        form = ProfileCompletionForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.profile_completed = True
            profile.save()
            return redirect(profile.get_dashboard_url())
    else:
        form = ProfileCompletionForm(instance=profile)

    return render(request, 'students/complete_profile.html', {'form': form})
        

# STUDENT: View materials

from accounts.models import StudyMaterial, Student
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def student_study_materials(request):
    student = get_object_or_404(Student, register_number=request.user.profile.register_number)
    branch = student.branch
    semester = student.semester

    materials = StudyMaterial.objects.filter(branch=branch, semester=semester).order_by('-uploaded_at')

    # Mark all fetched materials as seen
    student.seen_materials.add(*materials)

    return render(request, 'students/study_materials.html', {'materials': materials})


@login_required
def student_unseen_materials(request):
    student = get_object_or_404(Student, register_number=request.user.profile.register_number)
    
    unseen_count = StudyMaterial.objects.filter(
        branch=student.branch,
        semester=student.semester
    ).exclude(id__in=student.seen_materials.all()).count()

    return JsonResponse({"unseen_count": unseen_count})


def student_resources(request):
    branch = request.user.profile.branch
    semester = request.user.profile.semester

    # Get all materials for this branch and semester
    materials = StudyMaterial.objects.filter(branch=branch, semester=semester).order_by('-uploaded_at')

    # Split into categories using correct keys
    links = materials.filter(category='links')
    previous_qp = materials.filter(category='qp')
    study_notes = materials.filter(category='notes')

    context = {
        'links': links,
        'previous_quizzes': previous_qp,
        'study_notes': study_notes,
    }
    return render(request, 'students/resources.html', context)

from django.db.models import Count, Q
@login_required
def view_attendance(request):
    student = get_object_or_404(Student, register_number=request.user.profile.register_number)
    month = request.GET.get("month")

    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    
    if month:
        year, month_num = map(int, month.split("-"))
        attendance_records = attendance_records.filter(date__year=year, date__month=month_num)

    # Overall percentage
    total_classes = attendance_records.count()
    present_classes = attendance_records.filter(present=True).count()
    overall_attendance = round((present_classes / total_classes) * 100, 2) if total_classes > 0 else 0
    absent_percentage = 100 - overall_attendance  # <-- NEW

    # Subject-wise calculation
    subjects = Subject.objects.filter(branch=student.branch, semester=student.semester)
    subject_wise = {}
    for subject in subjects:
        subject_attendance = attendance_records.filter(subject=subject)
        total = subject_attendance.count()
        present = subject_attendance.filter(present=True).count()
        subject_wise[subject.name] = round((present / total) * 100, 2) if total > 0 else 0

    return render(request, 'students/view_attendance.html', {
        'attendance_records': attendance_records,
        'overall_attendance': overall_attendance,
        'absent_percentage': absent_percentage,  # <-- NEW
        'subject_wise': subject_wise,
        'selected_month': month
    })
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Attendance, Student, Subject



@login_required
def view_attendance(request):
    # Get student using logged-in user's profile register_number
    student = get_object_or_404(Student, register_number=request.user.profile.register_number)

    # Month filter
    month = request.GET.get("month")
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    if month:
        year, month_num = map(int, month.split("-"))
        attendance_records = attendance_records.filter(date__year=year, date__month=month_num)

    # Overall attendance
    total_classes = attendance_records.count()
    present_classes = attendance_records.filter(present=True).count()
    overall_attendance = round((present_classes / total_classes) * 100, 2) if total_classes > 0 else 0
    absent_percentage = 100 - overall_attendance

    # Subject-wise attendance
    subjects = Subject.objects.filter(branch=student.branch, semester=student.semester)
    subject_wise = {}
    for subject in subjects:
        subject_attendance = attendance_records.filter(subject=subject)
        total = subject_attendance.count()
        present = subject_attendance.filter(present=True).count()
        subject_wise[subject.name] = round((present / total) * 100, 2) if total > 0 else 0

    return render(request, 'students/view_attendance.html', {
        'attendance_records': attendance_records,
        'overall_attendance': overall_attendance,
        'absent_percentage': absent_percentage,
        'subject_wise': subject_wise,
        'selected_month': month
    })



# accounts/students/views.py
# accounts/students/views.py

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Assignment, AssignmentSubmission, Student
from django.shortcuts import render, get_object_or_404

from datetime import date

@login_required
def student_assignments(request):
    student = get_object_or_404(Student, register_number=request.user.profile.register_number)

    assignments = Assignment.objects.filter(
        subject__branch=student.branch,
        subject__semester=student.semester
    ).order_by('-created_at')

    submissions = AssignmentSubmission.objects.filter(student=student)
    submissions_dict = {sub.assignment.id: sub for sub in submissions}

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        file = request.FILES.get('file')
        assignment = get_object_or_404(Assignment, id=assignment_id)

        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student,
            file=file
        )
        messages.success(request, "Assignment submitted successfully!")
        return redirect('student_assignments')

    return render(request, 'students/assignments.html', {
        'assignments': assignments,
        'submissions': submissions,
        'submissions_dict': submissions_dict,
        'today': date.today()
    })

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import Assignment, AssignmentSubmission  # adjust if your models differ

@login_required

def student_unseen_assignments(request):
    student = get_object_or_404(Student, register_number=request.user.profile.register_number)

    # Assignments for student's branch & semester
    assignments = Assignment.objects.filter(
        subject__branch=student.branch,
        subject__semester=student.semester
    )

    # IDs of assignments already submitted by this student
    submitted_ids = AssignmentSubmission.objects.filter(
        student=student,
        assignment__in=assignments
    ).values_list('assignment_id', flat=True)

    # Count of assignments not yet submitted
    unseen_count = assignments.exclude(id__in=submitted_ids).count()

    return JsonResponse({"unseen_count": unseen_count})



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Subject, Doubt, DoubtMessage

@login_required
def student_chat(request):
    doubts = Doubt.objects.filter(student=request.user).order_by('-created_at')
    subjects = Subject.objects.all()
    return render(request, 'students/student_chat.html', {'doubts': doubts, 'subjects': subjects})

@login_required
def create_doubt(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id)
        doubt = Doubt.objects.create(student=request.user, teacher=subject.teacher, subject=subject)
        return JsonResponse({'doubt_id': doubt.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.utils.timezone import localtime

from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


@login_required
def get_messages(request, doubt_id):
    doubt = get_object_or_404(Doubt, id=doubt_id)
    # Mark current messages as read
    doubt.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages = doubt.messages.all().order_by('created_at')

    # Count unread messages for all doubts of this user
    unread_counts = {}
    for d in Doubt.objects.filter(student=request.user):
        unread_counts[d.id] = d.messages.filter(is_read=False).exclude(sender=request.user).count()

    data = {
        'messages': [
            {    
                'id': m.id,
                'sender': m.sender.username,
                'message': m.message,
                'file': m.file.url if m.file else None,
                'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_unsent': m.is_unsent
            } for m in messages
        ],
        'unread_counts': unread_counts
    }
    return JsonResponse(data)



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def student_unread_doubts(request):
    user = request.user  # logged-in student (User instance)

    # Get all doubts where this user is the student
    doubts = Doubt.objects.filter(student=user)

    # Count unread messages where sender is NOT this student
    unread_count = sum(
        d.messages.filter(is_read=False).exclude(sender=user).count()
        for d in doubts
    )

    return JsonResponse({"unread_count": unread_count})



@login_required
def send_message(request, doubt_id):
    if request.method == "POST":
        doubt = get_object_or_404(Doubt, id=doubt_id)
        content = request.POST.get('message', '').strip()
        file = request.FILES.get('file')

        if not content and not file:
            return JsonResponse({'error': 'Message or file required'}, status=400)

        msg = DoubtMessage.objects.create(
            doubt=doubt,
            sender=request.user,
            message=content if content else None,
            file=file
        )

        return JsonResponse({
            'id': msg.id,
            'sender': msg.sender.username,
            'message': msg.message,
            'file': msg.file.url if msg.file else None,
            'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_unsent': msg.is_unsent

        })
    return JsonResponse({'error': 'Invalid request'}, status=400)



@login_required
def unsend_doubt_message(request, message_id):
    try:
        msg = DoubtMessage.objects.get(id=message_id, sender=request.user)
        msg.is_unsent = True
        msg.message = None   # remove text
        msg.file = None      # remove file if attached
        msg.save()
        return JsonResponse({"status": "success"})
    except DoubtMessage.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Message not found"})
    

@login_required
def delete_doubt(request, doubt_id):
    if request.method == "POST":
        doubt = get_object_or_404(Doubt, id=doubt_id, student=request.user)
        doubt.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.models import Student, NoDues
from reportlab.pdfgen import canvas
from django.utils import timezone

@login_required
def check_dues(request):
    profile = request.user.profile

    # Ensure only students can access
    if profile.role != "student":
        return render(request, 'students/error.html', {
            'message': "Access denied. Please log in as a student."
        })

    student = Student.objects.filter(register_number=profile.register_number).first()
    if not student:
        return render(request, 'students/error.html', {
            'message': "Student record not found. Please contact admin."
        })

    dues = NoDues.objects.filter(student=student, has_dues=True)
    all_cleared = not dues.exists()

    return render(request, 'students/check_dues.html', {
        'dues': dues,
        'all_cleared': all_cleared,
    })


@login_required
def student_unseen_dues(request):
    student = Student.objects.get(register_number=request.user.profile.register_number)
    # Count dues that are still pending
    pending_dues = NoDues.objects.filter(student=student, has_dues=True).count()
    return JsonResponse({"unseen_count": pending_dues})


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

@login_required
def download_certificate(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return HttpResponse("Profile not found.", status=404)

    try:
        student = Student.objects.get(register_number=profile.register_number)
    except Student.DoesNotExist:
        return HttpResponse("Student profile not found.", status=404)

    dues_exist = NoDues.objects.filter(student=student, has_dues=True).exists()
    if dues_exist:
        return HttpResponse("You have pending dues. Cannot download certificate.", status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="NoDuesCertificate_{student.register_number}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - inch, "No Dues Clearance Certificate")

    # Body
    p.setFont("Helvetica", 12)
    y = height - inch * 1.5
    line_height = 18

    p.drawString(inch, y, f"Student Name: {student.name}")
    y -= line_height
    p.drawString(inch, y, f"Register Number: {student.register_number}")
    y -= line_height
    p.drawString(inch, y, f"Branch: {student.branch}")
    y -= line_height * 2

    p.drawString(inch, y, f"This is to certify that the above student has cleared all dues in the institution")
    y -= line_height
    p.drawString(inch, y, f"as of {timezone.now().strftime('%d-%m-%Y')}. This certificate is issued without any pending dues.")
    y -= line_height * 3

    # Signature placeholder
    p.drawString(inch, y, "Authorized Signature:")
    p.line(inch + 130, y - 5, inch + 300, y - 5)

    p.showPage()
    p.save()

    return response






# accounts/views.py

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import CGPARecord, Profile

@login_required
def cgpa_calculator(request):
    profile = Profile.objects.get(user=request.user)

    records = CGPARecord.objects.filter(user=request.user, department=profile.branch).order_by("semester")

    # prepare saved results to match JS expectation
    saved_results = {
        f"{profile.branch} - Semester {rec.semester}": {
            "sgpa": rec.sgpa,
            "totalCredits": rec.total_credits
        }
        for rec in records
    }

    return render(request, "students/cgpa_calculator.html", {
        "profile": profile,
        "saved_results": json.dumps(saved_results)
    })


@login_required
def save_sgpa(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            semester = int(data.get("semester"))
            sgpa = float(data.get("sgpa"))
            total_credits = int(data.get("total_credits"))

            profile = Profile.objects.get(user=request.user)

            CGPARecord.objects.update_or_create(
                user=request.user,
                department=profile.branch,
                semester=semester,
                defaults={"sgpa": sgpa, "total_credits": total_credits}
            )
            return JsonResponse({"success": True, "message": "SGPA saved!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})



@login_required
def clear_cgpa(request):
    if request.method == "POST":
        try:
            CGPARecord.objects.filter(user=request.user).delete()
            return JsonResponse({"success": True, "message": "All results cleared"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})
