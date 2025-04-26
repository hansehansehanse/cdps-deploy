from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password

from .models import CustomUser

import json
import uuid

import logging

emp_sidebar_items = [
    {'url':'hris_emp_dashboard', 'icon_class':'ti-smart-home', 'name':'Dashboard'},
    {'url':'hris_emp_records', 'icon_class':'ti-file', 'name':'Records'},
    {'url':'hris_emp_payroll', 'icon_class':'ti-file-dollar', 'name':'Payroll'},
    {'url':'hris_emp_leaves', 'icon_class':'ti-checkbox', 'name':'Leaves'},
]


#-------------------------------------------------------------------------
def cdps_admin_dashboard(request):
    # context = {'sidebar_items':emp_sidebar_items}
    context = {}
    return render(request, 'admin/dashboard.html', context)

def cdps_admin_dashboard2(request):
    # context = {'sidebar_items':emp_sidebar_items}
    context = {}
    return render(request, 'admin/dashboard2.html', context)

#-------------------------------------------------------------------------
#admin
def cdps_admin_accountManagement(request):
    # context = {'sidebar_items':emp_sidebar_items}
    context = {}
    return render(request, 'admin/accountManagement.html', context)


#-------------------------------------------------------------------------
#-------------------------------------------------------------------------

# from django.contrib.auth import get_user_model, login
# from django.contrib.auth.hashers import check_password
# from django.shortcuts import render, redirect
# from django.urls import reverse

# User = get_user_model()

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         # print("📨 Email entered:", email)
#         # print("🔐 Password entered:", password)

#         try:
#             user = User.objects.get(email=email)
#             print("👤 Match found in DB:", user)

#             if check_password(password, user.password):
#                 print("✅ Password matches!")
#                 print("🔎 Access level from DB:", user.access_level)

#                 login(request, user)

#                 if user.access_level == 'Admin':
#                     return redirect(reverse('account_management'))                  # !!!Update 
#                 elif user.access_level == 'Bus Manager':
#                     return redirect('cdps_admin_dashboard')                         # !!!Update
#                 else:
#                     print("❓ Unknown access level")
#                     return render(request, 'login.html', {'error': 'Access level not recognized'})
#             else:
#                 print("❌ Password does not match.")
#                 return render(request, 'login.html', {'error': 'Invalid password'})
#         except User.DoesNotExist:
#             print("❌ No user found with that email.")
#             return render(request, 'login.html', {'error': 'Invalid email'})

#     return render(request, 'login.html')

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_backends
from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            print("👤 Match found in DB:", user)

            if check_password(password, user.password):
                print("✅ Password matches!")
                print("🔎 Access level from DB:", user.access_level)

                # Explicitly specify the backend to avoid ValueError
                backend = get_backends()[0]
                login(request, user, backend=backend.__class__.__module__ + "." + backend.__class__.__name__)

                if user.access_level == 'Admin':
                    return redirect(reverse('account_management'))
                elif user.access_level == 'Bus Manager':
                    return redirect('cdps_admin_dashboard')
                else:
                    print("❓ Unknown access level")
                    return render(request, 'login.html', {'error': 'Access level not recognized'})
            else:
                print("❌ Password does not match.")
                return render(request, 'login.html', {'error': 'Invalid password'})
        except User.DoesNotExist:
            print("❌ No user found with that email.")
            return render(request, 'login.html', {'error': 'Invalid email'})

    return render(request, 'login.html')



#--


#--
# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError
# from django.contrib.auth import authenticate, login


# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         # Validate email format
#         try:
#             validate_email(email)  # Validates the email format
#         except ValidationError:
#             return render(request, 'login.html', {'error': 'Invalid email format'})

#         # Authenticate user
#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             login(request, user)
#             print(f"👤 Match found in DB: {user} ({user.user_code})")
#             print("✅ Password matches!")

#             if user.access_level == 'Admin':
#                 return redirect(reverse('account_management'))
#             elif user.access_level == 'Bus Manager':
#                 return redirect(reverse('bus_manager_dashboard'))
#             else:
#                 print("❓ Unknown access level")
#                 return render(request, 'login.html', {'error': 'Access level not recognized'})
#         else:
#             print("❌ No match or incorrect password")
#             return render(request, 'login.html', {'error': 'Invalid email or password'})

#     return render(request, 'login.html')


#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
# from django.shortcuts import render
# from .models import CustomUser

def user_list(request):
    print("✅ user_list being called")
    users = CustomUser.objects.all()
    print(f"🧾 Users in DB: {users}")
    return render(request, 'admin/accountManagement.html', {'users': users})

#-------------------------------------------------------------------------
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import CustomUser
# from django.contrib.auth.hashers import make_password  # To hash password before saving

# import json
# import uuid

logger = logging.getLogger(__name__)

def add_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("📩 Received data:", data)  # ADD THIS TO DEBUG

            user = CustomUser.objects.create_user(
                username=str(uuid.uuid4()),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', ''),
                phone_number=data.get('phone_number', ''),
                access_level=data.get('access_level', 'Bus Manager'),
                verified=data.get('verified', False),
                password=data.get('password', 'temporary123'),
            )

            return JsonResponse({'status': 'success'}, status=201)

        except Exception as e:
            print("❌ Exception:", e)
            logger.error(f"Error adding user: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Error occurred while adding user.'}, status=500)
        

        
        

#-------------------------------------------------------------------------
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from .models import CustomUser
# from django.contrib.auth.hashers import make_password

# @csrf_exempt  # only if you test without csrf token; otherwise keep csrf protection
def edit_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_code = data.get("user_code")
            user = CustomUser.objects.get(user_code=user_code)

            # Update fields
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.email = data["email"]
            user.phone_number = data["phone_number"]
            user.access_level = data["access_level"]
            user.verified = data["verified"]

            if data["password"]:  # Only update if password is provided
                user.password = make_password(data["password"])

            user.save()
            return JsonResponse({"message": "User updated successfully."})
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

#-------------------------------------------------------------------------
# from django.views.decorators.http import require_POST

@require_POST
def delete_user(request):
    try:
        data = json.loads(request.body)
        user_code = data.get("user_code")
        user = CustomUser.objects.get(user_code=user_code)
        user.delete()
        return JsonResponse({"message": "User deleted successfully."})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

#-------------------------------------------------------------------------

#-------------------------------------------------------------------------

#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
