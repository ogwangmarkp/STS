
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from users.models import User
from django.template.loader import render_to_string
from .models import Location

# Create your views here.

@csrf_exempt
@login_required
def location_list(request):
    locations = Location.objects.all()
    template = render_to_string(
        'locations/location_list.html', {'locations': locations})
    data = {
        'html': template,
        'status': 'success'
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
def location_form(request):
    if request.method == 'GET':
        action = request.GET.get('action', 'new')
        id = request.GET.get('id', None)

        if action == 'edit':
            location = Location.objects.get(pk=id)

            template = render_to_string(
                'locations/edit_location.html', {'location': location})
            
            data = {
                'html': template,
                'status': 'success'
            }
            return JsonResponse(data)


@csrf_exempt
@login_required
def save_location(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        id = request.POST.get('id', None)
        address = request.POST.get('address')

        if action == 'edit':
            location = Location.objects.filter(id=id).first()
            if location:
                location.address = address
                location.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Location.objects.create(**{
                "address":address,
                "added_by": User.objects.get(pk=1)
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
