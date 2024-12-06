
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from users.models import User
from django.template.loader import render_to_string
from .models import Supplier

# Create your views here.

@csrf_exempt
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    template = render_to_string(
        'suppliers/supplier_list.html', {'suppliers': suppliers})
    data = {
        'html': template,
        'status': 'success'
    }
    # suppliers.delete()
    return JsonResponse(data)


@csrf_exempt
@login_required
def supplier_form(request):
    if request.method == 'GET':
        action = request.GET.get('action', 'new')
        id = request.GET.get('id', None)

        if action == 'edit':
            supplier = Supplier.objects.get(pk=id)

            template = render_to_string(
                'suppliers/edit_supplier.html', {'supplier': supplier})
            
            data = {
                'html': template,
                'status': 'success'
            }
            return JsonResponse(data)


@csrf_exempt
@login_required
def save_supplier(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        id = request.POST.get('id', None)
        email = request.POST.get('email')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        phone_number_2 = request.POST.get('phone_number_2')

        if action == 'edit':
            supplier = Supplier.objects.filter(id=id).first()
            if supplier:
                supplier.email = email
                supplier.name = name
                supplier.address = address
                supplier.phone_number = phone_number
                supplier.phone_number_2 = phone_number_2
                supplier.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Supplier.objects.create(**{
                "email": email,
                "name": name,
                "address": address,
                "phone_number":phone_number,
                "phone_number_2":phone_number_2,
                "added_by": User.objects.get(pk=1)
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
