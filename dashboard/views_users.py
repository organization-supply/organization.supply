from django.shortcuts import render, redirect

def login(request):
    return render(request, 'users/login.html', {})

def logout(request):
    redirect('users_login')
