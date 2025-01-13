from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import User
from datetime import datetime

def user_login(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('/')
        else:
            messages.error(request, 'User not found.')

    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)

    return redirect('/accounts/login')

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        month = request.POST['month']
        day = request.POST['day']
        year = request.POST['year']

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'User already exists.')

            return redirect('register')

        try:
            birthday = datetime(month=int(month), day=int(day), year=int(year))
        except ValueError:
            birthday = None

        user = User.objects.create_user(username=username, email=email, password=password)
        user.birthday = birthday

        user.save()
        login(request, user)

        return redirect('/')

    return render(request, 'accounts/register.html')
