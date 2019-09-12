from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from threading import Thread
import os


def recovery(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email)
        if not user:
            return render(request, 'recovery.html', 
                {'error': 'Аккаунт с таким email не зарегестрирован'})
        user = user[0]
        current_site = get_current_site(request)
        message = render_to_string('acc_recovery.html', {
            'user':user, 'domain':current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        mail_subject = 'Смена пароля.'
        email = EmailMessage(mail_subject, message, to=[email])
        email.send()
        return HttpResponse('На указанный email выслано письмо для сброса пароля.')
    return render(request, 'recovery.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user':user, 'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            # Sending activation link in terminal
            # user.email_user(subject, message)
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Мы выслали письмо на указанный email. Перейдите по ссылке из письма для подтверждения регистрации.')
            # return render(request, 'acc_active_sent.html')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_v(request):
    form = UserLoginForm(request.POST or None)
    next = request.GET.get('next')
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('/')
    return render(request, "login.html", {'form': form})

def logout_v(request):
    logout(request)
    return redirect('/')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return HttpResponse('Activation link is invalid!')


def change_password(request, uidb64, token):
    if request.method == "POST":
        password = request.POST['password']
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        return redirect("/login/")
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        return render(request, "change_password.html")
    else:
        return HttpResponse('Activation link is invalid!')
