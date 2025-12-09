from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Student, NoDues
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from accounts.models import Student, NoDues


@login_required
def others_dashboard(request):
    # Always refresh user profile from DB
    profile = request.user.profile  # make sure this exists
    staff_department = profile.department if profile.department else 'Department'

    student = None
    dues = None
    register_number = request.GET.get('register_number')

    if register_number:
        student = Student.objects.filter(register_number=register_number).first()
        if student:
            dues = NoDues.objects.filter(student=student, department=staff_department)
        else:
            messages.error(request, "Student not found!")

    context = {
        'staff_department': staff_department,
        'student': student,
        'dues': dues,
    }
    return render(request, 'others/dashboard.html', context)
 


@login_required
@require_http_methods(["POST"])
def add_due(request):
    register_number = request.POST.get('register_number')
    remark = request.POST.get('remark')
    due_date = request.POST.get('due_date')

    department = getattr(request.user.profile, 'department', None)
    if not department:
        messages.error(request, "Your profile does not have a department assigned.")
        return redirect(f'/others/dashboard/?register_number={register_number}')

    student = get_object_or_404(Student, register_number=register_number)

    NoDues.objects.create(
        student=student,
        department=department,
        remark=remark,
        due_date=due_date if due_date else None, 
        has_dues=True,
        updated_by=request.user,
        updated_at=timezone.now(),
    )

    messages.success(request, f"Due added under {department}.")
    return redirect(f'/others/dashboard/?register_number={register_number}')


@login_required
@require_http_methods(["POST"])
def clear_all_dues(request):
    register_number = request.POST.get('register_number')
    student = get_object_or_404(Student, register_number=register_number)
    
    # Get logged in user's department (assuming in request.user.profile or similar)
    staff_department = request.user.profile.department
    
    # Delete dues ONLY for this student and this department
    NoDues.objects.filter(student=student, department=staff_department).delete()
    
    messages.success(request, f"All dues cleared for {staff_department} department.")
    return redirect(f'/others/dashboard/?register_number={register_number}')


@login_required
@require_http_methods(["POST"])
def clear_due(request, due_id):
    due = get_object_or_404(NoDues, id=due_id)

    # Safety: Only same department staff can clear
    if due.department != request.user.profile.department:
        messages.error(request, "You cannot clear dues from another department.")
        return redirect(f"/others/dashboard/?register_number={due.student.register_number}")

    due.has_dues = False
    due.save()

    messages.success(request, f"Due cleared for {due.student.register_number}.")
    return redirect(f"/others/dashboard/?register_number={due.student.register_number}")


from django.http import JsonResponse
from accounts.models import Student, NoDues

def ajax_search_student(request):
    reg = request.GET.get("register_number")

    if not reg:
        return JsonResponse({"status": "error"})

    try:
        student = Student.objects.get(register_number=reg)
    except Student.DoesNotExist:
        return JsonResponse({"status": "error"})

    dues = NoDues.objects.filter(student=student).order_by("-updated_at")

    dues_list = []
    for d in dues:
        dues_list.append({
            "id": d.id,
            "department": d.department,
            "has_dues": d.has_dues,
            "date": d.due_date.strftime("%m/%d/%Y") if d.due_date else "",
            "remark": d.remark if d.remark else "-",
            "updated_by": d.updated_by.username if d.updated_by else None,
            "updated_at": d.updated_at.strftime("%d %b %Y, %I:%M %p") if d.updated_at else None,
        })

    has_any_pending = dues.filter(has_dues=True).exists()

    # ✅ FIXED LAST UPDATED WITH LOCAL TIME
    latest_due = dues.order_by("-updated_at").first()

    if latest_due and latest_due.updated_at:
     local_time = timezone.localtime(latest_due.updated_at)
     last_updated_time = local_time.strftime("%d %b %Y, %I:%M %p")
    else:
        last_updated_time = None

    return JsonResponse({
        "status": "success",
        "student": {
            "name": student.name,
            "register_number": student.register_number,
            "branch": student.branch,
            "semester": student.semester,
        },
        "dues": dues_list,
        "has_any_pending": has_any_pending,
        "last_updated": last_updated_time
    })



