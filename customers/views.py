
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from users.models import User
from django.template.loader import render_to_string
from .models import Customer

# Create your views here.

@csrf_exempt
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    template = render_to_string(
        'customers/customer_list.html', {'customers': customers})
    data = {
        'html': template,
        'status': 'success'
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
def customer_form(request):
    if request.method == 'GET':
        action = request.GET.get('action', 'new')
        id = request.GET.get('id', None)

        if action == 'edit':
            customer = Customer.objects.get(pk=id)

            template = render_to_string(
                'customers/edit_customer.html', {'customer': customer})
            
            data = {
                'html': template,
                'status': 'success'
            }
            return JsonResponse(data)


@csrf_exempt
@login_required
def save_customer(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        id = request.POST.get('id', None)
        email = request.POST.get('email')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        phone_number_2 = request.POST.get('phone_number_2')

        if action == 'edit':
            customer = Customer.objects.filter(id=id).first()
            if customer:
                customer.email = email
                customer.name = name
                customer.address = address
                customer.phone_number = phone_number
                customer.phone_number_2 = phone_number_2
                customer.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Customer.objects.create(**{
                "email": email,
                "name": name,
                "address": address,
                "phone_number":phone_number,
                "phone_number_2":phone_number_2,
                "added_by": User.objects.get(pk=1)
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
