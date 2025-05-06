from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse
import requests
from .models import AppUser
from django.shortcuts import get_object_or_404


def home_view(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        weight = request.POST.get('weight')

        try:
            if int(age) >= 18 and int(weight) >= 50:
                messages.success(request, "You're eligible to donate!✅")
            else:
                messages.error(request, "Sorry, you're not eligible to donate ❌")
        except (ValueError, TypeError):
            messages.error(request, "Invalid input. Please enter valid numbers.")

        return redirect(reverse('home'))

    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if not name:
            messages.error(request, 'Name is required.')
        elif password != cpassword:
            messages.error(request, 'Passwords do not match')
        elif password.isalpha():
            messages.error(request, 'Password cannot be only letters. Include numbers or symbols.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already used')
        else:
            try:
                validate_password(password)
                user = User.objects.create_user(email=email, name=name, password=password)
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('login')
            except ValidationError as e:
                for error in e:
                    messages.error(request, error)
    return render(request, 'signup.html')




def login_view(request):
    if request.GET.get('next'):
        messages.warning(request, "⚠️ Please login before accessing the dashboard.")

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or 'dashboard')
        else:
            messages.error(request, 'Invalid Email or password')
    
    return render(request, 'login.html')

def about_view(request):
    # user_id = request.session.get("user_id")
    # user = get_object_or_404(AppUser, id=user_id)

    flask_api_url = "http://127.0.0.1:5000/about-us"

    try:
        response = requests.get(flask_api_url)
        print()
        if response.status_code == 200:
            about_info = response.json()
        else:
            about_info = {"error": "Could not fetch about us information"}
    except requests.exceptions.RequestException as e:
        about_info = {"error": f"Error occurred: {e}"}

    # return render(request, 'about.html', {
        # 'user': user,
        # 'about_info': about_info
    # })
    return render(request, 'about.html', {
        'about_info': about_info
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


