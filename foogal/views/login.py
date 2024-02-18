from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.http import HttpResponse
import json

def login(request):
    return render(request, 'login.html')


def login_view(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        username = params.get('username')
        password = params.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            return HttpResponse('success')

        else:
            return HttpResponse('failed')

    else:
        return redirect("home")