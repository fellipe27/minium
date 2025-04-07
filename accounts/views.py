from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from datetime import datetime

def login_page(request):
    if request.user.is_authenticated:
        return redirect('blog:home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('blog:home')
        else:
            messages.error(request, 'User not found.')

    return render(request, 'accounts/login_page.html')

def register_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        month = request.POST['month']
        day = request.POST['day']
        year = request.POST['year']

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            messages.error(request, 'User already exists.')

            return redirect('accounts:register')

        try:
            birthday = datetime(month=int(month), day=int(day), year=int(year))

            user = User.objects.create_user(username=username, email=email, password=password)
            user.birthday = birthday

            user.save()
            login(request, user)

            return redirect('blog:home')
        except ValueError:
            messages.error(request, 'Invalid birthday.')

    return render(request, 'accounts/register_page.html')

def user_logout(request):
    logout(request)

    return redirect('accounts:login')
