from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from .models import User
from django.template.loader import render_to_string
from django.contrib.auth import logout, authenticate, login 

import json
# Create your views here.
from django.contrib import messages 

def index(request):
    return redirect('/users/login/')

def login_user(request): 
    
    if request.method == 'GET':
        return render(request, 'login_page.html')

    if request.method == 'POST':
        username = request.POST.get('email') 
        password = request.POST.get('password') 

        if not (username and password): 
            messages.error(request, "Please provide all the details!!") 
            return render(request, 'login_page.html') 
        
        user = User.objects.filter(username=username, password=password).last() 
        if not user: 
            messages.error(request, 'Invalid Login Credentials!!') 
            return render(request, 'login_page.html') 
    
        login(request, user) 
        return redirect('/users/dashboard/') 

def logout_user(request): 
    logout(request) 
    return HttpResponseRedirect('/') 

@csrf_exempt
@login_required 
def user_dashboard(request): 
    if request.method == 'GET':
        return render(request, 'dashboard.html', {'user_role': ""}) 

@csrf_exempt
@login_required
def user_list(request):
    files = []
    file_list_template = render_to_string('users/user_list.html', {'files': files})
    
    data = {
        'html': file_list_template,
        'status': 'success'
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
def user_list(request):
    if request.method == 'GET':
        action = request.GET.get('action','list')
        id     = request.GET.get('id',None)

        if action == 'edit':
            user  = User.objects.filter(id=id).first()
            template   = render_to_string('users/edit_user.html', {'user': user})
            data = {
                'html':template,
                'status': 'success'
            }
            return JsonResponse(data)
        
        if action == 'list':   
            # Annotate User queryset with subquery
            users = User.objects.all()
            template = render_to_string('users/user_list.html', {'users': users})
            data = {
                'html':template,
                'status': 'success'
            }
            return JsonResponse(data)
        
    if request.method == 'POST':
        action = request.POST.get('action','save')
        id     = request.POST.get('id',None)
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        email      = request.POST.get('email')
        username   = request.POST.get('username')
        password   = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
       
        if action == 'edit':
            user  = User.objects.filter(id=id).first()
            user.first_name   = first_name
            user.last_name    = last_name
            user.email        = email
            user.phone_number = phone_number
            user.save()

            return JsonResponse({'status': 'success'})
        
        if action == 'save':
            saved_user = User.objects.create(**{
                "first_name":first_name,
                "last_name":last_name,
                 "password":password,
                "username":username,
                "phone_number":phone_number,
                "email":email,
            })

            if saved_user:
                return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
    