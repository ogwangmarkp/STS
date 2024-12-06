
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from users.models import User
from django.template.loader import render_to_string
from .models import *
from purchases.models import Purchase
from suppliers.models import Supplier
from django.db.models import F
from django.db.models import Subquery, OuterRef, Sum, FloatField, ExpressionWrapper
import datetime
from datetime import timedelta
from django.db.models.functions import Coalesce
# Create your views here.

@csrf_exempt
@login_required
def stock_list(request):   
    filter_start_date = request.GET.get('filter_start_date', None)
    filter_end_date = request.GET.get('filter_end_date', None)
    selected_supplier = request.GET.get('selected_supplier', None)
    suppliers = Supplier.objects.all()
    q_filter = {}

    if selected_supplier:
        q_filter['supplier__id'] = selected_supplier

    if filter_start_date:
        filter_start_date = datetime.datetime.strptime(filter_start_date, "%d-%m-%Y")

    if not filter_start_date:
        filter_start_date = datetime.date.today()
    
    if filter_end_date:
        filter_end_date = datetime.datetime.strptime(filter_end_date, "%d-%m-%Y")
    
    if not filter_end_date:
        filter_end_date = filter_start_date + timedelta(days=6)
    
    q_filter['record_date__date__gte'] = filter_start_date
    q_filter['record_date__date__lte'] = filter_end_date

    payment_at_subquery = Purchase.objects.filter(
        supplier=OuterRef('supplier'),  
        record_date__gte=filter_start_date,
        record_date__lte=filter_end_date  
    ).values('supplier').annotate(
        total=Sum(Coalesce('amount',0.0))  
    ).values('total')  

    expense_at_subquery = Stock.objects.filter(
        supplier=OuterRef('supplier'),
        record_date__gte=filter_start_date,
        record_date__lte=filter_end_date 
    ).values('supplier').annotate(
       total=Sum(Coalesce(F('quantity'),0.0) * Coalesce(F('price'),0.0),
    )
    ).values('total') 

    stock_list = Stock.objects.filter(**q_filter).annotate(
        payment_at = Coalesce(Subquery(payment_at_subquery),0.0),
        expense_at = Coalesce(Subquery(expense_at_subquery),0.0),     
    ).order_by('-record_date').annotate(
        balance=F('payment_at') - F('expense_at')
    )

    template = render_to_string(
        'purchases/stock_list.html', {
            'stock_list': stock_list,
            'selected_supplier':selected_supplier,
            'filter_start_date':filter_start_date,
            'filter_end_date':filter_end_date,
            'suppliers':suppliers,
        })
    data = {
        'html': template,
        'status': 'success'
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def stock_form(request):
    if request.method == 'GET':
        action = request.GET.get('action', 'new')
        id = request.GET.get('id', None)

        if action == 'edit':
            stock = Stock.objects.get(pk=id)
            suppliers = Supplier.objects.all()
            template = render_to_string(
                'purchases/edit_stock.html', {'stock': stock, 'suppliers':suppliers})
            
            data = {
                'html': template,
                'status': 'success'
            }
            return JsonResponse(data)


@csrf_exempt
@login_required
def save_stock(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        id = request.POST.get('id', None)
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        supplier_id = request.POST.get('supplier')
        record_date = request.POST.get('record_date')
        supplier = Supplier.objects.filter(id=supplier_id).first()
        
        if action == 'edit':
            stock = Stock.objects.filter(id=id).first()
            
            if stock:
                stock.quantity = quantity
                stock.price = price
                stock.supplier = supplier
                stock.record_date = datetime.strptime(record_date, '%d-%m-%Y')
                stock.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Stock.objects.create(**{
                "quantity": quantity,
                "price": price,
                "supplier":supplier,
                "record_date":datetime.strptime(record_date, '%d-%m-%Y'),
                "added_by": User.objects.get(pk=1)
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
    

@csrf_exempt
@login_required
def payment_list(request):
    filter_start_date = request.GET.get('filter_start_date', None)
    filter_end_date = request.GET.get('filter_end_date', None)
    selected_supplier = request.GET.get('selected_supplier', None)
    suppliers = Supplier.objects.all()
    q_filter = {}

    if selected_supplier:
        q_filter['supplier__id'] = selected_supplier

    if filter_start_date:
        filter_start_date = datetime.datetime.strptime(filter_start_date, "%d-%m-%Y")

    if not filter_start_date:
        filter_start_date = datetime.date.today()
    
    if filter_end_date:
        filter_end_date = datetime.datetime.strptime(filter_end_date, "%d-%m-%Y")
    
    if not filter_end_date:
        filter_end_date = filter_start_date + timedelta(days=6)
    
    q_filter['record_date__date__gte'] = filter_start_date
    q_filter['record_date__date__lte'] = filter_end_date

    payment_at_subquery = Purchase.objects.filter(
        supplier=OuterRef('supplier'),  
        record_date__gte=filter_start_date,
        record_date__lte=filter_end_date  
    ).values('supplier').annotate(
        total=Sum(Coalesce('amount',0.0))  
    ).values('total')  

    expense_at_subquery = Stock.objects.filter(
        supplier=OuterRef('supplier'),
        record_date__gte=filter_start_date,
        record_date__lte=filter_end_date  
    ).values('supplier').annotate(
       total=Sum(Coalesce(F('quantity'),0.0) * Coalesce(F('price'),0.0),
    )
    ).values('total') 
    payment_list = Purchase.objects.filter(**q_filter).annotate(
        payment_at = Coalesce(Subquery(payment_at_subquery),0.0),
        expense_at = Coalesce(Subquery(expense_at_subquery),0.0),      
    ).order_by("-record_date").annotate(
        balance=F('payment_at') - F('expense_at')
    )
 
    template = render_to_string(
        'purchases/payment_list.html', {
            'purchases': payment_list,
            'selected_supplier':selected_supplier,
            'filter_start_date':filter_start_date,
            'filter_end_date':filter_end_date,
            'suppliers':suppliers
        })
    data = {
        'html': template,
        'status': 'success'
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
def payment_form(request):
    if request.method == 'GET':
        action = request.GET.get('action', 'new')
        id = request.GET.get('id', None)

        if action == 'edit':
            purchase = Purchase.objects.get(pk=id)
            suppliers = Supplier.objects.all()
            template = render_to_string(
                'purchases/edit_payment.html', {'purchase': purchase, 'suppliers':suppliers})
            
            data = {
                'html': template,
                'status': 'success'
            }
            return JsonResponse(data)


@csrf_exempt
@login_required
def save_payment(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        id = request.POST.get('id', None)
        amount = request.POST.get('amount')
        supplier_id = request.POST.get('supplier')
        record_date = request.POST.get('record_date')
        supplier = Supplier.objects.filter(id=supplier_id).first()
        
        if action == 'edit':
            purchase = Purchase.objects.filter(id=id).first()
            
            if purchase:
                purchase.amount = amount
                purchase.supplier = supplier
                purchase.record_date = datetime.strptime(record_date, '%d-%m-%Y')
                purchase.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Purchase.objects.create(**{
                "amount": amount,
                "supplier":supplier,
                "record_date":datetime.strptime(record_date, '%d-%m-%Y'),
                "added_by": User.objects.get(pk=1)
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})