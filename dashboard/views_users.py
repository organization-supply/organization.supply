from django.shortcuts import render, redirect

def login(request):
    return render(request, 'users/login.html', {})

def logout(request):
    return redirect('users_login')
