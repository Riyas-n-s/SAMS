from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Profile, Subject,Student,Attendance
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import Staff  # adjust path to your actual Staff model



def teacher_profile(request):
    profile = request.user.profile  # or however you get the teacher profile
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'teachers/profile.html', context)



# -------------------------------
# SUBJECT MANAGEMENT
# -------------------------------

@login_required
def add_subject(request):
    if request.method == "POST":
        code = request.POST.get('code')
        name = request.POST.get('name')
        semester = request.POST.get('semester')
        branch = request.POST.get('branch')

        if code and name and semester and branch:
            Subject.objects.create(
                code=code,
                name=name,
                semester=semester,
                branch=branch,
                teacher=request.user
            )
            messages.success(request, "Subject added successfully!")
            return redirect('add_subject')
        else:
            messages.error(request, "All fields are required.")

    subjects = Subject.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'teachers/add_subject.html', {'subjects': subjects})

@login_required
def edit_subject(request, id):
    subject = get_object_or_404(Subject, id=id, teacher=request.user)
    if request.method == "POST":
        subject.code = request.POST.get('code')
        subject.name = request.POST.get('name')
        subject.semester = request.POST.get('semester')
        subject.branch = request.POST.get('branch')
        subject.save()
        messages.success(request, "Subject updated successfully!")
        return redirect('add_subject')
    return render(request, 'teachers/edit_subject.html', {'subject': subject})

@login_required
def delete_subject(request, id):
    subject = get_object_or_404(Subject, id=id, teacher=request.user)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect('add_subject')


# -------------------------------
# STUDY MATERIAL MANAGEMENT
# -------------------------------

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import StudyMaterial, Subject
from accounts.models import Profile  # adjust if Profile is in another app

# TEACHER: Upload
@login_required
def upload_and_manage_study_material(request):
    subjects = Subject.objects.filter(teacher=request.user)
    materials = StudyMaterial.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')

    if request.method == "POST":
        title = request.POST.get('title')
        category = request.POST.get('category')
        subject_id = request.POST.get('subject')
        link = request.POST.get('link')
        file = request.FILES.get('file')

        subject = Subject.objects.get(id=subject_id)
        semester = subject.semester
        branch = subject.branch  # auto-filled from subject

        StudyMaterial.objects.create(
            title=title,
            category=category,
            subject=subject,
            semester=semester,
            branch=branch,
            link=link if category == 'links' else None,
            file=file if category != 'links' else None,
            uploaded_by=request.user
        )
        messages.success(request, "Study material uploaded successfully!")
        return redirect('upload_and_manage_study_material')  # reload same page

    return render(request, 'teachers/upload_and_manage_study_material.html', {
        'subjects': subjects,
        'materials': materials
    })


login_required
def delete_study_material(request, material_id):
    if request.method == "POST":
        material = get_object_or_404(StudyMaterial, id=material_id, uploaded_by=request.user)
        material.delete()
        messages.success(request, "Study material deleted successfully.")
    return redirect('upload_and_manage_study_material')




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import Student, Subject, Attendance

@login_required
def mark_attendance(request):
    subjects = Subject.objects.filter(teacher=request.user)
    students = Student.objects.all().order_by('roll_number')  # Roll no ascending

    if request.method == "POST":
        date = request.POST.get('date')
        hour = request.POST.get('hour')
        subject_id = request.POST.get('subject')
        topic = request.POST.get('topic')
        present_ids = request.POST.getlist('present')

        subject = get_object_or_404(Subject, id=subject_id)

        for student in students:
            present = str(student.id) in present_ids
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=date,
                hour=hour,
                defaults={'present': present, 'topic': topic, 'marked_by': request.user}
            )

        messages.success(request, "Attendance saved successfully!")
        return redirect('mark_attendance')

    return render(request, 'teachers/mark_attendance.html', {
        'students': students,
        'subjects': subjects
    })
@login_required
def mark_attendance(request):
    subjects = Subject.objects.filter(teacher=request.user)

    # Get selected subject id from GET (for filtering)
    selected_subject_id = request.GET.get('subject')

    students = Student.objects.none()  # default empty queryset
    selected_semester = ''

    if selected_subject_id:
        # Fetch the subject for semester info
        subject = get_object_or_404(Subject, id=selected_subject_id)
        selected_semester = subject.semester

        # Filter students by that semester only
        students = Student.objects.filter(semester=selected_semester).order_by('roll_number')
    else:
        # If no subject selected, optionally show no students or all students (choose one)
        students = Student.objects.none()

    if request.method == "POST":
        date = request.POST.get('date')
        hour = request.POST.get('hour')
        subject_id = request.POST.get('subject')
        topic = request.POST.get('topic')
        present_ids = request.POST.getlist('present')

        subject = get_object_or_404(Subject, id=subject_id)

        # Only mark attendance for students currently filtered
        # Or you can fetch all students for that semester again
        marked_students = Student.objects.filter(semester=subject.semester)

        for student in marked_students:
            present = str(student.id) in present_ids
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=date,
                hour=hour,
                defaults={'present': present, 'topic': topic, 'marked_by': request.user}
            )

        messages.success(request, "Attendance saved successfully!")
        # Redirect back preserving GET parameters to keep filter
        redirect_url = f"{request.path}?subject={subject_id}&date={date}&hour={hour}&topic={topic}"
        return redirect(redirect_url)

    return render(request, 'teachers/mark_attendance.html', {
        'students': students,
        'subjects': subjects,
        'selected_subject_id': selected_subject_id,
        'selected_semester': selected_semester,
    })


# accounts/teachers/views.py
from accounts.models import Assignment, Subject
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
# accounts/teachers/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Assignment, AssignmentSubmission, Subject

@login_required
def teacher_assignments(request):
    subjects = Subject.objects.filter(teacher=request.user)
    assignments = Assignment.objects.filter(created_by=request.user).order_by('-created_at')

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        file = request.FILES.get('file')

        Assignment.objects.create(
            subject_id=subject_id,
            title=title,
            description=description,
            due_date=due_date,
            file=file,
            created_by=request.user
        )
        ##messages.success(request, "Assignment created successfully!")
        return redirect('teacher_assignments')

    return render(request, 'teachers/assignments.html', {'subjects': subjects, 'assignments': assignments})


@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)

    if request.method == "POST":
        sub_id = request.POST.get("submission_id")
        marks = request.POST.get("marks")
        remarks = request.POST.get("remarks")

        submission = get_object_or_404(AssignmentSubmission, id=sub_id)
        submission.marks = marks
        submission.remarks = remarks
        submission.status = 'graded'
        submission.save()

        messages.success(request, "Marks & remarks updated successfully!")
        return redirect('view_submissions', assignment_id=assignment.id)

    return render(request, 'teachers/submissions.html', {'assignment': assignment, 'submissions': submissions})


@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    assignment.delete()
    #messages.success(request, "Assignment deleted successfully!")
    return redirect('teacher_assignments')



# ---------- TEACHER ----------

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import Subject, Doubt  # make sure Message model is imported
from django.http import JsonResponse

from django.utils.timezone import localtime

from django.utils.timezone import localtime

@login_required
def teacher_chat(request, doubt_id=None):
    subjects = Subject.objects.filter(teacher=request.user)
    doubts = Doubt.objects.filter(subject__in=subjects).order_by('-created_at')

    unread_counts = {}
    for d in doubts:
        unread_counts[d.id] = d.messages.filter(is_read=False).exclude(sender=request.user).count()
        last_msg = d.messages.order_by('-created_at').first()
        if last_msg:
            last_msg.created_at = localtime(last_msg.created_at).strftime('%Y-%m-%d %H:%M')
        d.last_message = last_msg

    return render(request, 'teachers/teacher_chat.html', {
        'doubts': doubts,
        'unread_counts': unread_counts,
        'selected_doubt': doubt_id
    })

from django.http import JsonResponse
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required

@login_required
def teacher_doubt_messages(request, doubt_id):
    doubt = Doubt.objects.get(id=doubt_id)
    
    # Messages for this doubt
    messages = doubt.messages.order_by('created_at')
    msgs = []
    for m in messages:
        msgs.append({
            "sender": m.sender.username,
            "message": m.message,
            "file": m.file.url if m.file else None,
            "created_at": localtime(m.created_at).strftime('%Y-%m-%d %H:%M')
        })
    
    # Unread counts for all doubts
    subjects = Subject.objects.filter(teacher=request.user)
    doubts = Doubt.objects.filter(subject__in=subjects)
    unread_counts = {}
    for d in doubts:
        unread_counts[d.id] = d.messages.filter(is_read=False).exclude(sender=request.user).count()
    
    return JsonResponse({"messages": msgs, "unread_counts": unread_counts})



@login_required
def teacher_unread_counts(request):
    subjects = Subject.objects.filter(teacher=request.user)
    doubts = Doubt.objects.filter(subject__in=subjects)
    unread_counts = {}
    for d in doubts:
        count = d.messages.filter(is_read=False).exclude(sender=request.user).count()
        if count > 0:
            unread_counts[d.id] = count
    return JsonResponse({"unread_counts": unread_counts})


@login_required
def teacher_dashboard(request):
    return render(request, 'teachers/dashboard.html')
