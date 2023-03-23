import os
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from users.models import User
from users.forms import LoginForm

def valid_captcha(request):
    recaptcha = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': os.environ.get('CAPTCHA'),
        'response': recaptcha,
        'remoteip': None
    }
    return requests.post(url, data=data).json()['success'] == True

def login_view(request):
    loginForm = LoginForm()

    if request.user.is_authenticated:
        return redirect('/')
       
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            if valid_captcha(request):                                                           
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    _next = request.GET.get('next')
                    if _next is not None:
                        return redirect(_next)
                    return redirect('/')
                if not User.objects.filter(username=os.environ.get('SUPERUSER_USERNAME')).exists():
                    User.objects.create_superuser(os.environ.get('SUPERUSER_USERNAME'), os.environ.get('SUPERUSER_EMAIL'), os.environ.get('SUPERUSER_PASSWORD'))
                messages.add_message(request, messages.ERROR, 'Usuário ou senha inválidos!', extra_tags='danger')
                return redirect('/')
            messages.add_message(request, messages.ERROR, 'Por gentileza, preencha o reCAPTCHA corretamente!', extra_tags='danger')
            return redirect('/')
    return render(request, 'auth/login.html', {'form': loginForm})

def logout_view(request):
    logout(request)
    return redirect('/auth/login')