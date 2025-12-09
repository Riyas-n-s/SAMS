from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.models import Student
from django.urls import reverse


def is_admin_user(user):
    return user.is_superuser or user.is_staff

from accounts.models import Student, Staff, OthersStaff
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin_user(user):
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):

    # ✅ REQUIRED FOR STUDENT TABLE
    students = Student.objects.all().order_by('register_number')

    # ✅ FIXED COUNTS
    total_students = Student.objects.count()
    total_staff = Staff.objects.count()              # ✅ TEACHERS
    total_others_staff = OthersStaff.objects.count() # ✅ OTHERS

    context = {
        "students": students,
        "total_students": total_students,
        "total_staff": total_staff,
        "total_others_staff": total_others_staff,
    }

    return render(request, "admin_panel/dashboard.html", context)


    

@login_required
@user_passes_test(is_admin_user)
def upgrade_semesters(request):
    if request.method == 'POST':
        students = Student.objects.filter(semester__lt=6)
        count = students.count()
        for student in students:
            student.semester += 1
            student.save()
        messages.success(request, f"Semester upgraded for {count} students.")
        return redirect(reverse('admin_panel:admin_dashboard') + '?section=manageStudents')

    return redirect('admin_panel:admin_dashboard')
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentForm, StudentBulkUploadForm
from accounts.models import Student


# --- Add individual student ---
def add_student(request):
    
    form = StudentForm(request.POST or None)  # Keep POST data in the form

    if request.method == "POST":
        if form.is_valid():
            reg_no = form.cleaned_data['register_number']
            if Student.objects.filter(register_number=reg_no).exists():
                messages.error(request, "Student with this Register Number already exists!")
                # Just render the same template with the filled form
                students = Student.objects.all().order_by('register_number')
                return render(
                    request,
                    "admin_panel/add_student.html",
                    {"form": form, "students": students, "section": "addStudents"}
                )
            else:
                form.save()
                messages.success(request, "Student added successfully!")
                return redirect(reverse('admin_panel:admin_dashboard') + '?section=manageStudents')

    # GET request
    students = Student.objects.all().order_by('register_number')
    return render(
        request,
        "admin_panel/add_student.html",
        {"form": form, "students": students, "section": "addStudents"}
    )
# --- Bulk upload students ---

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import pandas as pd
from accounts.models import Student
from .forms import StudentBulkUploadForm

def bulk_upload_students(request):
    form = StudentBulkUploadForm(request.POST or None, request.FILES or None)
    added, skipped, invalid_rows = 0, 0, []  # track added, skipped, invalid
    duplicate_students = []

    if request.method == "POST" and form.is_valid():
        file = request.FILES.get("file")
        if not file or not file.name.endswith(".csv"):
            messages.error(request, "Please upload a CSV file only.")
        else:
            try:
                df = pd.read_csv(file)

                # Required headers in exact order
                required_headers = ["register_number", "name", "branch", "semester", "roll_number"]
                
                # Strict header order check
                if list(df.columns) != required_headers:
                    messages.error(
                        request,
                        f"Invalid CSV format! Headers must be exactly: {', '.join(required_headers)}"
                    )
                else:
                    allowed_branches = ["CT", "ELS", "CSE", "ECE"]  # adjust as needed

                    for idx, row in df.iterrows():
                        line_no = idx + 2  # CSV line number
                        reg_no = str(row["register_number"]).strip()
                        name = str(row["name"]).strip()
                        branch = str(row["branch"]).strip()
                        semester = row["semester"]
                        roll_number = row["roll_number"]

                        # Row validation
                        invalid = False
                        if not reg_no.isdigit() or len(reg_no) != 8:
                            invalid = True
                        elif not all(x.isalpha() or x.isspace() for x in name):
                            invalid = True
                        elif branch not in allowed_branches:
                            invalid = True
                        try:
                            semester = int(semester)
                            roll_number = int(roll_number)
                        except:
                            invalid = True

                        if invalid:
                            invalid_rows.append(line_no)
                            continue

                        # Check duplicates
                        if Student.objects.filter(register_number=reg_no).exists():
                            skipped += 1
                            duplicate_students.append({
                                "register_number": reg_no,
                                "name": name,
                                "branch": branch,
                                "semester": semester,
                                "roll_number": roll_number,
                            })
                        else:
                            Student.objects.create(
                                register_number=reg_no,
                                name=name,
                                branch=branch,
                                semester=semester,
                                roll_number=roll_number
                            )
                            added += 1

                    # Show messages
                    if added:
                        messages.success(request, f"{added} student(s) added successfully!")
                    if skipped:
                        messages.warning(request, f"{skipped} student(s) skipped (already exist).")
                    if invalid_rows:
                        messages.error(
                            request,
                            f"Improperly formatted row(s): {', '.join(map(str, invalid_rows))}"
                        )

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")

        # Redirect only if students added successfully
        if added > 0 and not invalid_rows:
            return redirect(reverse('admin_panel:admin_dashboard') + '?section=manageStudents')

    return render(
        request,
        "admin_panel/bulk_upload_students.html",
        {
            "form": form,
            "duplicate_students": duplicate_students,
            "invalid_rows": invalid_rows
        }
    )

    

# --- Add individual student ---




from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from accounts.models import Student, Profile
from .forms import StudentForm

# --------------------------
# Edit Student
# --------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Student, Profile
from .forms import StudentForm

def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()  # save student changes

            # --- Update Profile by register_number ---
            try:
                profile = Profile.objects.get(register_number=student.register_number)
                profile.name = student.name
                profile.branch = student.branch
                profile.semester = student.semester
                profile.save()
                print(f"✅ Profile updated for Student {student.register_number}")
            except Profile.DoesNotExist:
                print(f"❌ No Profile found for Student {student.register_number}")

            messages.success(request, "✅ Student & Profile updated successfully!")
            return redirect(reverse('admin_panel:admin_dashboard') + '?section=manageStudents')
        else:
            print(form.errors)
    else:
        form = StudentForm(instance=student)

    return render(request, "admin_panel/edit_student.html", {"form": form})



# --------------------------
# Delete Student
# --------------------------
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Student, Profile



def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        try:
            # Delete linked Profile and User safely
            profile = Profile.objects.filter(register_number=student.register_number).first()
            if profile:
                if profile.user:
                    profile.user.delete()  # Delete linked User
                    print(f"✅ User deleted for Student {student.register_number}")
                profile.delete()  # Delete Profile
                print(f"✅ Profile deleted for Student {student.register_number}")

            # Delete the Student
            student.delete()
            messages.success(request, f"✅ Student {student.register_number} and related data deleted successfully!")

        except Exception as e:
            messages.error(request, f"❌ Error deleting student: {e}")

        return redirect(reverse('admin_panel:admin_dashboard') + '?section=manageStudents')


    # GET request: show confirmation page
    return render(request, "admin_panel/confirm_delete.html", {"student": student})

 

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Staff, OthersStaff

def manage_all_staff(request):
    staffs = Staff.objects.all()
    others_staffs = OthersStaff.objects.all()
    
    return render(request, 'admin_panel/manage_all_staff.html', {
        'staffs': staffs,
        'others_staffs': others_staffs
    })


#



def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)

    if request.method == "POST":
        # --- Update Staff fields ---
        staff.name = request.POST.get('name')
        staff.staff_id = request.POST.get('staff_id')
        staff.department = request.POST.get('department')
        staff.save()
        print(f"✅ Staff {staff.staff_id} updated successfully!")

        # --- Update Profile by staff_id ---
        try:
            profile = Profile.objects.get(staff_id=staff.staff_id)
            profile.name = staff.name
            profile.department = staff.department
            profile.save()
            print(f"✅ Profile updated for Staff {staff.staff_id}")
        except Profile.DoesNotExist:
            print(f"⚠️ No Profile found for Staff {staff.staff_id}")

        messages.success(request, "✅ Staff & Profile updated successfully!")
        return redirect("admin_panel:manage_all_staff")

    # GET request → pre-fill form manually in template
    return render(request, "admin_panel/edit_staff.html", {"staff": staff})



def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)

    if request.method == "POST":
        try:
            # Delete linked Profile safely (if exists)
            profile = Profile.objects.filter(staff_id=staff.staff_id).first()
            if profile:
                if profile.user:
                    profile.user.delete()
                    print(f"✅ User deleted for Staff {staff.staff_id}")
                profile.delete()
                print(f"✅ Profile deleted for Staff {staff.staff_id}")
            else:
                print(f"⚠️ No Profile found for Staff {staff.staff_id}")

            # Delete the Staff record (always)
            staff.delete()
            messages.success(request, f"✅ Staff {staff.staff_id} deleted successfully!")

        except Exception as e:
            messages.error(request, f"❌ Error deleting Staff: {e}")

        return redirect("admin_panel:manage_all_staff")

    # GET request: show confirmation page
    return render(request, "admin_panel/confirm_delete_staff.html", {"staff": staff})


def edit_others_staff(request, others_id):
    other = get_object_or_404(OthersStaff, id=others_id)
    
    if request.method == "POST":
        # --- Update OthersStaff fields ---
        other.name = request.POST.get('name')
        other.staff_id = request.POST.get('staff_id')
        other.staff_in_charge = request.POST.get('staff_in_charge')
        other.save()

        # --- Update Profile by staff_id ---
        try:
            profile = Profile.objects.get(staff_id=other.staff_id)
            profile.name = other.name
            profile.department = other.staff_in_charge
            profile.save()
            print(f"✅ Profile updated for OthersStaff {other.staff_id}")
        except Profile.DoesNotExist:
            print(f"❌ No Profile found for OthersStaff {other.staff_id}")

        messages.success(request, "✅ Others Staff & Profile updated successfully!")
        return redirect("admin_panel:manage_all_staff")
    
    return render(request, "admin_panel/edit_others_staff.html", {"other": other})


from accounts.models import OthersStaff, Profile

def delete_others_staff(request, others_id):
    other = get_object_or_404(OthersStaff, id=others_id)

    if request.method == "POST":
        try:
            # Delete linked Profile and User safely
            profile = Profile.objects.filter(staff_id=other.staff_id).first()
            if profile:
                if profile.user:
                    profile.user.delete()  # Delete linked User
                    print(f"✅ User deleted for OthersStaff {other.staff_id}")
                profile.delete()  # Delete Profile
                print(f"✅ Profile deleted for OthersStaff {other.staff_id}")

            # Delete the OthersStaff record
            other.delete()
            messages.success(request, f"✅ OthersStaff {other.staff_id} and related data deleted successfully!")

        except Exception as e:
            messages.error(request, f"❌ Error deleting OthersStaff: {e}")

        return redirect("admin_panel:manage_all_staff")

    # GET request: show confirmation page
    return render(request, "admin_panel/confirm_delete_others_staff.html", {"other": other})


import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Staff, OthersStaff, Student
from .forms import (
    StudentForm, StaffForm, OthersStaffForm,
    StudentBulkUploadForm, StaffBulkUploadForm, OthersStaffBulkUploadForm
)

# ------------------ Individual Add Views ------------------


def add_staff(request):
    form = StaffForm(request.POST or None)
    existing_staff = None  # store matching staff if found

    if request.method == "POST":
        if form.is_valid():
            staff_id = form.cleaned_data.get("staff_id")

            # Check if staff already exists
            if Staff.objects.filter(staff_id=staff_id).exists():
                existing_staff = Staff.objects.get(staff_id=staff_id)
                messages.error(request, "Staff with this Staff ID already exists!")
            else:
                form.save()
                messages.success(request, "✅ Staff added successfully!")
                return redirect(reverse('admin_panel:manage_all_staff'))

    return render(
        request,
        "admin_panel/add_staff.html",
        {"form": form, "existing_staff": existing_staff}
    )




def add_others_staff(request):
    form = OthersStaffForm(request.POST or None)
    existing_staff = None

    if request.method == "POST":
        if form.is_valid():
            staff_id = form.cleaned_data.get("staff_id")
            existing_staff = OthersStaff.objects.filter(staff_id=staff_id).first()

            if existing_staff:
                messages.error(request, "Other Staff with this Staff ID already exists!")
                return render(
                    request,
                    "admin_panel/others_add.html",  # ✅ use correct template name
                    {"form": form, "existing_staff": existing_staff, "section": "addOthersStaff"}
                )
            else:
                form.save()
                messages.success(request, "Other Staff added successfully!")
                return redirect('admin_panel:manage_all_staff')  # ✅ use URL name

    return render(
        request,
        "admin_panel/others_add.html",  # ✅ consistent template name
        {"form": form, "existing_staff": existing_staff, "section": "addOthersStaff"}
    )

# ------------------ Bulk CSV Upload Views ------------------

def upload_staff_csv(request):
    form = StaffBulkUploadForm(request.POST or None, request.FILES or None)
    errors_found = False
    added, skipped = 0, 0
    duplicate_staff = []  # store skipped staff details

    if request.method == 'POST' and form.is_valid():
        csv_file = request.FILES.get('file')

        # Check CSV extension
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "❌ Please upload a valid CSV file.")
            errors_found = True
        else:
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)
                required_headers = {"name", "staff_id", "department"}

                # Validate headers
                if set(df.columns) != required_headers:
                    messages.error(
                        request,
                        f"❌ Invalid CSV format! Headers must be: {', '.join(required_headers)}"
                    )
                    errors_found = True
                else:
                    for idx, row in df.iterrows():
                        # Prevent row with missing columns
                        if len(row) != len(required_headers):
                            messages.error(request, f"❌ Row {idx + 2} has incorrect number of columns.")
                            continue

                        staff_id = str(row['staff_id']).strip()
                        if Staff.objects.filter(staff_id=staff_id).exists():
                            skipped += 1
                            duplicate_staff.append({
                                "name": row["name"],
                                "staff_id": staff_id,
                                "department": row["department"],
                            })
                        else:
                            Staff.objects.create(
                                name=row['name'].strip(),
                                staff_id=staff_id,
                                department=row['department'].strip()
                            )
                            added += 1

                    if skipped:
                        messages.warning(request, f"{skipped} staff(s) skipped (already exist).")

            except Exception as e:
                messages.error(request, f"❌ Error processing file: {e}")
                errors_found = True

        # Redirect only if at least one staff added and no errors
        if added > 0 and not errors_found:
            messages.success(request, f"{added} staff(s) added successfully!")
            return redirect('admin_panel:manage_all_staff')
        elif added == 0 and skipped > 0:
            errors_found = True  # stay on page to show duplicates

    return render(
        request,
        'admin_panel/staff_csv.html',
        {
            "form": form,
            "duplicate_staff": duplicate_staff  # pass to template to show skipped staff
        }
    )


# ===================== OTHERS STAFF CSV UPLOAD =====================

import csv
from io import TextIOWrapper

def upload_others_staff_csv(request):
    form = OthersStaffBulkUploadForm(request.POST or None, request.FILES or None)
    duplicate_others_staff = []
    added, skipped = 0, 0

    if request.method == 'POST' and form.is_valid():
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "❌ Please upload a valid CSV file.")
        else:
            try:
                decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                reader = csv.DictReader(decoded_file)

                # ✅ Preventive: check headers
                required_headers = ["name", "staff_id", "staff_in_charge"]
                if reader.fieldnames != required_headers:
                    messages.error(
                        request,
                        f"❌ Invalid CSV headers! Must be exactly: {', '.join(required_headers)}"
                    )
                else:
                    for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header
                        # Check row length matches header
                        if len(row) != len(required_headers):
                            messages.error(
                                request,
                                f"❌ Row {row_num} has incorrect number of columns."
                            )
                            continue

                        staff_id = row['staff_id'].strip()
                        if OthersStaff.objects.filter(staff_id=staff_id).exists():
                            skipped += 1
                            duplicate_others_staff.append(row)
                        else:
                            OthersStaff.objects.create(
                                name=row['name'].strip(),
                                staff_id=staff_id,
                                staff_in_charge=row['staff_in_charge'].strip()
                            )
                            added += 1

                    if skipped:
                        messages.warning(request, f"{skipped} other staff(s) skipped (already exist).")
                    if added:
                        messages.success(request, f"{added} other staff(s) added successfully!")

            except Exception as e:
                messages.error(request, f"❌ Error processing CSV: {e}")

    return render(
        request,
        'admin_panel/upload_others_staff_csv.html',
        {
            'form': form,
            'duplicate_others_staff': duplicate_others_staff
        }
    )



def a(request):
    """
    Your intermediate staff page.
    """
    return render(request, 'admin_panel/a.html')



