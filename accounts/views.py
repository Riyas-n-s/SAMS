from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.hashers import make_password
from twilio.rest import Client
from .models import Profile, Staff,Student,OthersStaff # <-- Removed Student

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# --- Utility: Mask phone ---
def mask_phone(phone):
    return "******" + phone[-4:] if phone else None

# --- Step 1: Forgot Password - Get Username & Send OTP ---
def send_otp(request):
    username = request.GET.get("username") or request.POST.get("username")
    phone = masked_phone = None

    if not username:
        messages.error(request, "Username is required.")
        return redirect('login')

    try:
        user = User.objects.get(username=username)
        phone = user.profile.phone
        if phone:
            masked_phone = mask_phone(phone)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    if request.method == "POST":
        if not phone:
            messages.error(request, "No phone number linked to this account.")
            return redirect('send_otp')
        # Send OTP via Twilio
        client.verify.services(settings.TWILIO_VERIFY_SID).verifications.create(
            to=phone,
            channel='sms'
        )
        request.session['reset_username'] = username
        request.session['reset_phone'] = phone
        return redirect('verify_otp')

    return render(request, "accounts/send_otp.html", {'username': username, 'masked_phone': masked_phone})

# --- Step 2: Verify OTP ---
def verify_otp(request):
    phone = request.session.get('reset_phone')
    masked_phone = mask_phone(phone)

    if not phone:
        messages.error(request, "Session expired. Please try again.")
        return redirect('send_otp')

    if request.method == "POST":
        otp = request.POST.get("otp")
        try:
            verification_check = client.verify.services(settings.TWILIO_VERIFY_SID).verification_checks.create(
                to=phone,
                code=otp
            )
            if verification_check.status == "approved":
                return redirect('set_new_password')
            else:
                messages.error(request, "Invalid OTP.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, "accounts/verify_otp.html", {"masked_phone": masked_phone})

# --- Step 3: Set New Password ---
def set_new_password(request):
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('set_new_password')

        username = request.session.get('reset_username')
        try:
            user = User.objects.get(username=username)
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    return render(request, "accounts/set_new_password.html")

# --- Registration ---
##def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        role = request.POST.get('role')
        id_number = request.POST.get('id_number')
        phone = request.POST.get('phone')

        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})

        name = branch = department = semester = None
        if role == "student":
            # Get details from Profile directly (no Student model now)
            try:
                existing_profile = Profile.objects.get(register_number=id_number, role="student")
                name = existing_profile.name
                branch = existing_profile.branch
                semester = existing_profile.semester
            except Profile.DoesNotExist:
                return render(request, 'accounts/register.html', {'error': 'Student record not found'})
        elif role in ["teacher", "others"]:
            try:
                staff = Staff.objects.get(staff_id=id_number)
                name = staff.name
                department = staff.department
            except Staff.DoesNotExist:
                return render(request, 'accounts/register.html', {'error': 'Staff record not found'})
        elif role == "admin":
            name = "Administrator"

        user = User.objects.create_user(username=username, password=password, email=email)
        profile = user.profile
        profile.role = role
        profile.name = name
        profile.phone = phone
        profile.register_number = id_number if role == "student" else None
        profile.staff_id = id_number if role in ["teacher", "others"] else None
        profile.branch = branch
        profile.department = department
        profile.semester = semester
        profile.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')
##def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        role = request.POST.get('role')
        id_number = request.POST.get('id_number')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        branch = request.POST.get('branch')
        semester = request.POST.get('semester')
        department = request.POST.get('department')

        # Password check
        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        # Username check
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})

        # Handle student
        if role == "student":
            student, created = Student.objects.get_or_create(
                register_number=id_number,
                defaults={'name': name, 'branch': branch, 'semester': semester}
            )
            if not created:
                student.name = name
                student.branch = branch
                student.semester = semester
                student.save()
            branch = student.branch
            semester = student.semester

        # Handle teacher staff
        elif role == "teacher":
            staff, created = Staff.objects.get_or_create(
                staff_id=id_number,
                defaults={'name': name, 'department': department}
            )
            if not created:
                staff.name = name
                staff.department = department
                staff.save()
            department = staff.department

        # Handle others staff
        elif role == "others":
            other_staff, created = OthersStaff.objects.get_or_create(
                staff_id=id_number,
                defaults={'name': name, 'staff_in_charge': department}  # Use 'department' field for staff_in_charge
            )
            if not created:
                other_staff.name = name
                other_staff.staff_in_charge = department
                other_staff.save()
            department = other_staff.staff_in_charge # or keep as you wish

        elif role == "admin":
            name = "Administrator"

        # Create user and profile
        user = User.objects.create_user(username=username, password=password, email=email)
        profile = user.profile
        profile.role = role
        profile.name = name
        profile.phone = phone
        profile.register_number = id_number if role == "student" else None
        profile.staff_id = id_number if role in ["teacher", "others"] else None
        profile.branch = branch if role == "student" else None
        profile.department = department if role ==["teacher", "others"]else None
        profile.semester = semester if role == "student" else None
        profile.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')
from django.contrib import messages
from django.shortcuts import render, redirect
from accounts.models import Student, Staff, OthersStaff, Profile

def register(request):
    if request.method == "POST":
        role = request.POST.get('role')
        id_number = request.POST.get('id_number')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        branch = request.POST.get('branch')
        semester = request.POST.get('semester')
        department = request.POST.get('department')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password check
        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        # Check if already registered in Profile
        if Profile.objects.filter(register_number=id_number).exists() or Profile.objects.filter(staff_id=id_number).exists():
            return render(request, 'accounts/register.html', {'error': 'User already registered!'})

        # Save into Profile table
        
        user = User.objects.create_user(username=username, password=password, email=email)
        profile = user.profile
        profile.role = role
        profile.name = name
        profile.phone = phone
        profile.register_number = id_number if role == "student" else None
        profile.staff_id = id_number if role in ["teacher", "others"] else None
        profile.branch = branch
        profile.department = department
        profile.semester = int(semester) if role == "student" and semester else None
        profile.save()
        ##profile.semester = semester
        ##profile.save()

        profile.save()
        messages.success(request, "Registration successful!")
        return redirect('login')

    return render(request, 'accounts/register.html')

from django.http import JsonResponse
from accounts.models import Student, Staff, OthersStaff, Profile

def get_user_details(request):
    user_id = request.GET.get('id')
    role = request.GET.get('role')

    # --- Check if already registered in Profile ---
    if role == "student" and Profile.objects.filter(register_number=user_id).exists():
        return JsonResponse({'error': 'Student already registered'}, status=400)
    elif role in ["teacher", "others"] and Profile.objects.filter(staff_id=user_id).exists():
        return JsonResponse({'error': 'User already registered'}, status=400)

    # --- Fetch details from your tables ---
    if role == 'student':
        try:
            student = Student.objects.get(register_number=user_id)
            return JsonResponse({
                'name': student.name,
                'branch': student.branch,
                'semester': student.semester
            })
        except Student.DoesNotExist:
            return JsonResponse({'error': 'No student found'}, status=404)

    elif role == 'teacher':
        try:
            staff = Staff.objects.get(staff_id=user_id)
            return JsonResponse({
                'name': staff.name,
                'department': staff.department
            })
        except Staff.DoesNotExist:
            return JsonResponse({'error': 'No teacher found'}, status=404)

    elif role == 'others':
        try:
            other_staff = OthersStaff.objects.get(staff_id=user_id)
            return JsonResponse({
                'name': other_staff.name,
                'department': getattr(other_staff, 'department', None) or getattr(other_staff, 'staff_in_charge', None)
            })
        except OthersStaff.DoesNotExist:
            return JsonResponse({'error': 'No other staff found'}, status=404)

    return JsonResponse({'error': 'Invalid role'}, status=400)

               
# --- Login ---S
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(user.profile.get_dashboard_url())
        return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})
    return render(request, 'accounts/login.html')

# --- Logout ---
def user_logout(request):
    logout(request)
    return redirect('login')

# --- Dashboards ---

@login_required
def student_dashboard(request):
    profile = request.user.profile
    student_data = profile.student  # still works if profile is linked

    if not student_data:
         # If student field is empty, try reverse lookup
        student_data = Student.objects.filter(user=request.user).first()
        if not student_data:
            return render(request, 'accounts/found.html', status=404)

    return render(request, 'accounts/student_dashboard.html', {'student': student_data})


@login_required
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')

@login_required
def others_dashboard(request):
    return render(request, 'others/dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')


# accounts/views.py

from django.shortcuts import render, get_object_or_404
from .models import Profile  # or wherever your Profile model is

def teacher_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'teachers/profile.html', {'profile': profile, 'user': request.user})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.models import Student

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    students = Student.objects.all().order_by('register_number')
    return render(request, 'admin_panel/dashboard.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def upgrade_semester(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        if student.semester < 6:
            student.semester += 1
            student.save()
            messages.success(request, f"{student.name}'s semester upgraded to {student.semester}")
        else:
            messages.warning(request, f"{student.name} is already in the maximum semester (6)")
    return redirect('accounts:admin_dashboard')


def home(request):
    return render(request, 'accounts/home.html')

def test (request):
    return render(request, 'accounts/test.html')

def contact(request):
    return render(request, 'accounts/contact.html')


def about(request):
    return render(request, 'accounts/about.html')

def terms(request):
    return render(request, 'accounts/terms.html')


def privacy(request):
    return render(request, 'accounts/privacy.html')


def loader_page(request, next_url):
    """
    Dynamic loader page.
    `next_url` is the name of the URL pattern to redirect to.
    """
    context = {
        'next_url': next_url
    }
    return render(request, 'accounts/loader.html', context)
