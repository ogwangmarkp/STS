
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from users.models import User
from django.template.loader import render_to_string
from suppliers.models import Supplier
import datetime
from datetime import timedelta
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from purchases.models import Stock
from.helper import generate_days_with_weekday
# Create your views here.

@csrf_exempt
@login_required
def weekly_reports(request):
    supplier_ids = []
    report_data = []
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    selected_supplier = request.GET.get('selected_supplier', None)
    suppliers = Supplier.objects.all()

    if selected_supplier:
        supplier_ids = Supplier.objects.filter(id=selected_supplier).values_list('id', flat=True)
    else:
        supplier_ids = Supplier.objects.all().values_list('id', flat=True)
    
    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%d-%m-%Y")

    if not start_date:
        start_date = datetime.date.today()
    
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    
    if not end_date:
        end_date = start_date + timedelta(days=6)

    days_list = generate_days_with_weekday(start_date, end_date)
    filtered_supplier_list = Supplier.objects.filter(id__in=supplier_ids)
    if filtered_supplier_list:
        for filtered_supplier in filtered_supplier_list:
            supplier_data = []
            for day_data in days_list:
                quantity = '---'
                stock_list = Stock.objects.filter(
                    supplier=filtered_supplier,
                    record_date__date__gte=datetime.datetime.strptime(day_data['date'], "%d-%m-%Y"),
                    record_date__date__lte=datetime.datetime.strptime(day_data['date'], "%d-%m-%Y")).annotate(total=Sum(Coalesce(F('quantity'),0.0))    
                ).values('total') 
                if stock_list:
                    quantity = stock_list[0]['total']
                supplier_data.append({'date':day_data['date'],
                                'weekday':f"{day_data['date']}, {day_data['weekday']}",
                                'quantity':quantity})
            report_data.append({'name':filtered_supplier.name,'supplier_data':supplier_data}) 
    template = render_to_string(
        'reports/periodic_reports.html', {'suppliers': suppliers,'selected_supplier':selected_supplier,'start_date':start_date,'end_date':end_date,'days_list':days_list,'report_data':report_data})
    data = {
        'html': template,
        'status': 'success'
    }
    return JsonResponse(data)

