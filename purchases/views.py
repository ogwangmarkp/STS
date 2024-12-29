
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
import datetime
import json
from datetime import timedelta
from django.db.models import Subquery, OuterRef, Sum,  Case, When, Value, FloatField
from django.db.models.functions import Coalesce,Round
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
        record_date__lte=OuterRef('record_date'),   
    ).values('supplier').annotate(
        total=Sum(Coalesce('amount',0.0))  
    ).values('total')  

    latest_price_subquery = Stock.objects.filter(
         supplier=OuterRef('supplier'),
         record_date__lte=OuterRef('record_date'),
    ).order_by('-record_date').values('price')[:1]
    
    qty_at_subquery = Stock.objects.filter(
        supplier=OuterRef('supplier'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('supplier').annotate(
       total=Sum(Coalesce(F('quantity'),0.0))
    ).values('total') 

    expense_at_subquery = Stock.objects.filter(
        supplier=OuterRef('supplier'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('supplier').annotate(
       total=Sum(Coalesce(F('quantity'),0.0) * Coalesce(F('price'),0.0),
    )
    ).values('total') 

    stock_list = Stock.objects.filter(**q_filter).annotate(
        payment_at = Coalesce(Subquery(payment_at_subquery),0.0),
        expense_at = Coalesce(Subquery(expense_at_subquery),0.0),  
        qty_at = Coalesce(Subquery(qty_at_subquery),0.0),   
        latest_price = Coalesce(Subquery(latest_price_subquery),1.0),    
    ).order_by('-record_date').annotate(
        balance=F('payment_at') - F('expense_at'),
        balance_qty =Round(( F('payment_at') - F('expense_at'))/Case(
        When(latest_price=0, then=Value(1)),
        default='latest_price',
        output_field=FloatField()
    ),2)
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
        amount_paid = request.POST.get('amount_paid',None)
        supplier_id = request.POST.get('supplier')
        record_date = request.POST.get('record_date')
        supplier = Supplier.objects.filter(id=supplier_id).first()
        
        if action == 'edit':
            stock = Stock.objects.filter(id=id).first()
            
            if stock:
                stock.quantity = quantity
                stock.price = price
                stock.supplier = supplier
                stock.record_date = datetime.datetime.strptime(record_date, '%d-%m-%Y')
                stock.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Stock.objects.create(**{
                "quantity": quantity,
                "price": price,
                "supplier":supplier,
                "record_date":datetime.datetime.strptime(record_date, '%d-%m-%Y'),
                "added_by": request.user
            })

            # Capture payments
            if amount_paid  and float(amount_paid) > 0:
                Purchase.objects.create(**{
                    "amount": float(amount_paid),
                    "supplier":supplier,
                    "record_date":datetime.datetime.strptime(record_date, '%d-%m-%Y'),
                    "added_by": request.user
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
        record_date__lte=OuterRef('record_date'), 
    ).values('supplier').annotate(
        total=Sum(Coalesce('amount',0.0))  
    ).values('total')  

    latest_price_subquery = Stock.objects.filter(
         supplier=OuterRef('supplier'),
         record_date__lte=OuterRef('record_date'),
    ).order_by('-record_date').values('price')[:1]
    
    qty_at_subquery = Stock.objects.filter(
        supplier=OuterRef('supplier'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('supplier').annotate(
       total=Sum(Coalesce(F('quantity'),0.0))
    ).values('total') 

    expense_at_subquery = Stock.objects.filter(
        supplier=OuterRef('supplier'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'), 
    ).values('supplier').annotate(
       total=Sum(Coalesce(F('quantity'),0.0) * Coalesce(F('price'),0.0),
    )
    ).values('total') 
    payment_list = Purchase.objects.filter(**q_filter).annotate(
        payment_at = Coalesce(Subquery(payment_at_subquery),0.0),
        expense_at = Coalesce(Subquery(expense_at_subquery),0.0), 
        qty_at = Coalesce(Subquery(qty_at_subquery),0.0),   
        latest_price = Coalesce(Subquery(latest_price_subquery),1.0),     
    ).order_by("-record_date").annotate(
        balance=F('payment_at') - F('expense_at'),
        balance_qty =Round(( F('payment_at') - F('expense_at'))/Case(
        When(latest_price=0, then=Value(1)),
        default='latest_price',
        output_field=FloatField()
    ),2)
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
                purchase.record_date = datetime.datetime.strptime(record_date, '%d-%m-%Y')
                purchase.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Purchase.objects.create(**{
                "amount": amount,
                "supplier":supplier,
                "record_date":datetime.datetime.strptime(record_date, '%d-%m-%Y'),
                "added_by": request.user
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})


@csrf_exempt
@login_required
def bulk_stocking(request):
    if request.method == 'GET':
        template = request.GET.get('template')
        
        Json_data = [['Supplier No','Supplier Name','Quantity','Price','Record Date','Amount Paid']]
        
        if template == 'payment':
          Json_data = [['Supplier No','Supplier Name','Record Date','Amount Paid']]
          
        suppliers = Supplier.objects.all()
        if suppliers:
            for supplier in suppliers:
                if template == 'payment':
                    Json_data.append([supplier.supplier_no,supplier.name,"",""])
                else:
                    Json_data.append([supplier.supplier_no,supplier.name,"","","",""])
                    
        
        data = {
            'Json_data': Json_data,
            'status': 'success'
        }
        # suppliers.delete()
        return JsonResponse(data)
    
    if request.method == 'POST':
        stock_purchases = request.POST.get('stock_purchases')
        stock_purchases = json.loads(stock_purchases)
       
        if stock_purchases:
            for stock_purchase in stock_purchases:
                supplier_no = stock_purchase.get('Supplier No',None)
                quantity = stock_purchase.get('Quantity',None)
                price = stock_purchase.get('Price',None)
                record_date = stock_purchase.get('Record Date',None)
                amount_paid = stock_purchase.get('Amount Paid',None)
               
                if supplier_no and quantity and price and record_date:
                    Stock.objects.create(**{
                        "quantity": quantity,
                        "price": price,
                        "supplier":Supplier.objects.filter(supplier_no=supplier_no).first(),
                        "record_date":datetime.datetime.strptime(record_date, '%Y-%m-%d'),
                        "added_by": request.user
                    })
                
                if supplier_no and record_date and amount_paid and float(amount_paid) > 0:
                    Purchase.objects.create(**{
                        "amount": amount_paid,
                        "supplier":Supplier.objects.filter(supplier_no=supplier_no).first(),
                        "record_date":datetime.datetime.strptime(record_date, '%Y-%m-%d'),
                        "added_by": request.user
                    })
            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'failed'})