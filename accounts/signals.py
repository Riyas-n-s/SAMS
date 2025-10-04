from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student, Staff, OthersStaff, Profile

# --------------------------
# Create Profile automatically when User is created
# --------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from accounts.models import Student, Profile
from django.contrib.auth.models import User

# --------------------------
# Update or create Profile automatically when Student is saved
# --------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, Profile

@receiver(post_save, sender=Student)
def sync_profile_with_student(sender, instance, **kwargs):
    try:
        # Find the existing Profile by register_number
        profile = Profile.objects.get(register_number=instance.register_number)
        profile.name = instance.name
        profile.branch = instance.branch
        profile.semester = instance.semester
        profile.save()
        print(f"✅ Profile updated for Student {instance.register_number}")
    except Profile.DoesNotExist:
        print(f"❌ No Profile found for Student {instance.register_number}")

# --------------------------
# Delete Profile & User automatically when Student is deleted
# --------------------------


# --------------------------
# Delete Profile & User automatically when Student is deleted
# --------------------------
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Student, Profile

@receiver(post_delete, sender=Student)
def delete_linked_profile_and_user(sender, instance, **kwargs):
    try:
        # 1️⃣ Delete Profile linked by register_number
        Profile.objects.filter(register_number=instance.register_number).delete()
        print(f"✅ Profile deleted for Student {instance.register_number}")

        # 2️⃣ Delete linked User
        if instance.user:
            instance.user.delete()
            print(f"✅ User deleted for Student {instance.register_number}")

    except Exception as e:
        print(f"❌ Error deleting linked Profile/User for {instance.register_number}: {e}")



# --------------------------
# Update Profile automatically when Staff is saved
# --------------------------
#@receiver(post_save, sender=Staff)
#def update_profile_from_staff(sender, instance, **kwargs):
    if instance.user:
        profile, _ = Profile.objects.get_or_create(user=instance.user)
        profile.department = instance.department
        profile.save()
        print(f"✅ Profile updated from Staff {instance.staff_id}")
@receiver(post_save, sender=Staff)
def sync_profile_with_staff(sender, instance, **kwargs):
    try:
        profile = Profile.objects.get(staff_id=instance.staff_id)
        profile.name = instance.name
        profile.department = instance.department
        profile.save()
        print(f"✅ [Signal] Profile updated for Staff {instance.staff_id}")
    except Profile.DoesNotExist:
        print(f"❌ [Signal] No Profile found for Staff {instance.staff_id}")

# --------------------------
# Update Profile automatically when OthersStaff is saved
# --------------------------
#@receiver(post_save, sender=OthersStaff)
#def update_profile_from_othersstaff(sender, instance, **kwargs):
    if instance.user:
        profile, _ = Profile.objects.get_or_create(user=instance.user)
        profile.department = instance.staff_in_charge
        profile.save()
        print(f"✅ Profile updated from OthersStaff {instance.staff_id}")
@receiver(post_save, sender=OthersStaff)
def sync_profile_with_others_staff(sender, instance, **kwargs):
    try:
        profile = Profile.objects.get(staff_id=instance.staff_id)
        profile.name = instance.name
        profile.department = instance.staff_in_charge  # mapping staff_in_charge to department
        profile.save()
        print(f"✅ [Signal] Profile updated for OthersStaff {instance.staff_id}")
    except Profile.DoesNotExist:
        print(f"❌ [Signal] No Profile found for OthersStaff {instance.staff_id}")

# --------------------------


# --------------------------
# Delete Profile & User when Staff is deleted
# --------------------------
#@receiver(pre_delete, sender=Staff)
#def delete_profile_when_staff_deleted(sender, instance, **kwargs):
    if instance.user:
        user = instance.user
        instance.user = None
        instance.save()
        Profile.objects.filter(user=user).delete()
        user.delete()
        print(f"🗑️ Deleted Profile & User for Staff {instance.staff_id}")
from django.db.models.signals import post_delete
from django.dispatch import receiver
from accounts.models import Staff, Profile

@receiver(post_delete, sender=Staff)
def delete_linked_profile_and_user_for_staff(sender, instance, **kwargs):
    try:
        # 1️⃣ Delete linked User first
        if instance.user:
            instance.user.delete()
            print(f"✅ User deleted for Staff {instance.staff_id}")

        # 2️⃣ Delete Profile linked by staff_id
        deleted, _ = Profile.objects.filter(staff_id=instance.staff_id).delete()
        if deleted:
            print(f"✅ Profile deleted for Staff {instance.staff_id}")
        else:
            print(f"⚠️ No Profile found for Staff {instance.staff_id}")

    except Exception as e:
        print(f"❌ Error deleting linked Profile/User for Staff {instance.staff_id}: {e}")

# --------------------------
# Delete Profile & User when OthersStaff is deleted
# --------------------------
#@receiver(pre_delete, sender=OthersStaff)
#def delete_profile_when_othersstaff_deleted(sender, instance, **kwargs):
    if instance.user:
        user = instance.user
        instance.user = None
        instance.save()
        Profile.objects.filter(user=user).delete()
        user.delete()
        print(f"🗑️ Deleted Profile & User for OthersStaff {instance.staff_id}")
from django.db.models.signals import post_delete
from django.dispatch import receiver
from accounts.models import OthersStaff, Profile

@receiver(post_delete, sender=OthersStaff)
def delete_linked_profile_and_user_for_others(sender, instance, **kwargs):
    try:
        # 1️⃣ Delete linked User first
        if instance.user:
            instance.user.delete()
            print(f"✅ User deleted for OthersStaff {instance.staff_id}")

        # 2️⃣ Delete Profile linked by staff_id
        deleted, _ = Profile.objects.filter(staff_id=instance.staff_id).delete()
        if deleted:
            print(f"✅ Profile deleted for OthersStaff {instance.staff_id}")
        else:
            print(f"⚠️ No Profile found for OthersStaff {instance.staff_id}")

    except Exception as e:
        print(f"❌ Error deleting linked Profile/User for OthersStaff {instance.staff_id}: {e}")
