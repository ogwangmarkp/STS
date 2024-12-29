
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from users.models import User
from django.template.loader import render_to_string
from .models import Customer
from locations.models import Location
# Create your views here.

@csrf_exempt
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('customer_no')
    locations = Location.objects.all()
    template = render_to_string(
        'customers/customer_list.html', {'customers': customers,'locations':locations})
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
            locations = Location.objects.all()
            template = render_to_string(
                'customers/edit_customer.html', {'customer': customer,'locations':locations})
            
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
        phone_number = request.POST.get('phone_number')
        phone_number_2 = request.POST.get('phone_number_2')
        address = Location.objects.filter(id=request.POST.get('address')).first()

        if action == 'edit':
            customer = Customer.objects.filter(id=id).first()
            if customer:
                customer_no = customer.customer_no

                if not customer_no:
                    customer_no = f'CN{customer.id}'
                    customer.customer_no = customer_no

                customer.email = email
                customer.name = name
                customer.address = address
                customer.phone_number = phone_number
                customer.phone_number_2 = phone_number_2
                customer.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            # Generate Customer Number
            customer_no = 'CN1'
            last_customer = Customer.objects.all().order_by('id').last()
            
            if last_customer:
                customer_no = f'CN{last_customer.id + 1}'

            Customer.objects.create(**{
                "customer_no":customer_no,
                "email": email,
                "name": name,
                "address": address,
                "phone_number":phone_number,
                "phone_number_2":phone_number_2,
                "added_by": User.objects.get(pk=1)
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
