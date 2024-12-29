
from django.http import  JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from users.models import User
from django.template.loader import render_to_string
from .models import *
from customers.models import Customer
from django.db.models import F
from django.db.models import Subquery, OuterRef, Sum,  Case, When, Value, FloatField
from django.db.models.functions import Coalesce,Round
import json
import datetime
from datetime import timedelta
# Create your views here.


@csrf_exempt
@login_required
def sale_list(request):    
    filter_start_date = request.GET.get('filter_start_date', None)
    filter_end_date = request.GET.get('filter_end_date', None)
    selected_customer = request.GET.get('selected_customer', None)
    customers = Customer.objects.all()
    q_filter = {}

    if selected_customer:
        q_filter['customer__id'] = selected_customer

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

    payment_at_subquery = Sale.objects.filter(
        customer=OuterRef('customer'),  
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),  
    ).values('customer').annotate(
        total=Sum(Coalesce('amount',0.0))  
    ).values('total')  
    
    latest_price_subquery = StockDelivered.objects.filter(
         customer=OuterRef('customer'),
         record_date__lte=OuterRef('record_date'),
    ).order_by('-record_date').values('price')[:1]
    
    qty_at_subquery = StockDelivered.objects.filter(
        customer=OuterRef('customer'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('customer').annotate(
       total=Sum(Coalesce(F('quantity'),0.0))
    ).values('total') 

    expense_at_subquery = StockDelivered.objects.filter(
        customer=OuterRef('customer'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('customer').annotate(
       total=Sum(Coalesce(F('quantity'),0.0) * Coalesce(F('price'),0.0),
    )
    ).values('total') 

    sales_list = StockDelivered.objects.filter(**q_filter).annotate(
        payment_at = Coalesce(Subquery(payment_at_subquery),0.0),
        expense_at = Coalesce(Subquery(expense_at_subquery),0.0),  
        qty_at = Coalesce(Subquery(qty_at_subquery),0.0),   
        latest_price = Coalesce(Subquery(latest_price_subquery),1.0),    
    ).order_by('-record_date').annotate(
        balance= F('expense_at')-F('payment_at'),
        balance_qty =Round(( F('expense_at') - F('payment_at'))/Case(
        When(latest_price=0, then=Value(1)),
        default='latest_price',
        output_field=FloatField()
    ),2)
    )
    
    template = render_to_string(
        'sales/sales_list.html', {
            'sales_list': sales_list,
            'customers':customers,
            'selected_customer':selected_customer,
            'filter_start_date':filter_start_date,
            'filter_end_date':filter_end_date
            })
    data = {
        'html': template,
        'status': 'success'
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def sale_form(request):
    if request.method == 'GET':
        action = request.GET.get('action', 'new')
        id = request.GET.get('id', None)

        if action == 'edit':
            sale = StockDelivered.objects.get(pk=id)
            customers = Customer.objects.all()
            template = render_to_string(
                'sales/edit_sale.html', {'sale': sale, 'customers':customers})
            
            data = {
                'html': template,
                'status': 'success'
            }
            return JsonResponse(data)


@csrf_exempt
@login_required
def save_sale(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        id = request.POST.get('id', None)
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        amount_paid = request.POST.get('amount_paid',None)
        customer_id = request.POST.get('customer')
        record_date = request.POST.get('record_date')
        customer = Customer.objects.filter(id=customer_id).first()
        
        if action == 'edit':
            sale = StockDelivered.objects.filter(id=id).first()
            
            if sale:
                sale.quantity = quantity
                sale.price = price
                sale.customer = customer
                sale.record_date = datetime.datetime.strptime(record_date, '%d-%m-%Y')
                sale.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            StockDelivered.objects.create(**{
                "quantity": quantity,
                "price": price,
                "customer":customer,
                "record_date":datetime.datetime.strptime(record_date, '%d-%m-%Y'),
                "added_by": request.user
            })

            # Capture payments
            if amount_paid  and float(amount_paid) > 0:
                Sale.objects.create(**{
                    "amount": float(amount_paid),
                    "customer":customer,
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
    selected_customer = request.GET.get('selected_customer', None)
    customers = Customer.objects.all()
    q_filter = {}

    if selected_customer:
        q_filter['customer__id'] = selected_customer

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
  
    latest_price_subquery = StockDelivered.objects.filter(
         customer=OuterRef('customer'),
         record_date__lte=OuterRef('record_date'),
    ).order_by('-record_date').values('price')[:1]
    
    qty_at_subquery = StockDelivered.objects.filter(
        customer=OuterRef('customer'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('customer').annotate(
       total=Sum(Coalesce(F('quantity'),0.0))
    ).values('total') 

    payment_at_subquery = Sale.objects.filter(
        customer=OuterRef('customer'),  
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'), 
    ).values('customer').annotate(
        total=Sum(Coalesce('amount',0.0))  
    ).values('total')  

    expense_at_subquery = StockDelivered.objects.filter(
        customer=OuterRef('customer'),
        record_date__gte=filter_start_date,
        record_date__lte=OuterRef('record_date'),
    ).values('customer').annotate(
       total=Sum(Coalesce(F('quantity'),0.0) * Coalesce(F('price'),0.0),
    )
    ).values('total') 
    payment_list = Sale.objects.filter(**q_filter).annotate(
        payment_at = Coalesce(Subquery(payment_at_subquery),0.0),
        expense_at = Coalesce(Subquery(expense_at_subquery),0.0), 
        qty_at = Coalesce(Subquery(qty_at_subquery),0.0),   
        latest_price = Coalesce(Subquery(latest_price_subquery),1.0),     
    ).order_by("-record_date").annotate(
        balance= F('expense_at')-F('payment_at'),
        balance_qty =Round(( F('expense_at') - F('payment_at'))/Case(
        When(latest_price=0, then=Value(1)),
        default='latest_price',
        output_field=FloatField()
    ),2)
    )
 
    template = render_to_string(
        'sales/payment_list.html', {
            'sales': payment_list,
            'customers':customers,
            'selected_customer':selected_customer,
            'filter_start_date':filter_start_date,
            'filter_end_date':filter_end_date
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
            sale = Sale.objects.get(pk=id)
            customers = Customer.objects.all()
            template = render_to_string(
                'sales/edit_payment.html', {'sale': sale, 'customers':customers})
            
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
        customer_id = request.POST.get('customer')
        record_date = request.POST.get('record_date')
        customer = Customer.objects.filter(id=customer_id).first()
        
        if action == 'edit':
            sale = Sale.objects.filter(id=id).first()
            
            if sale:
                sale.amount = amount
                sale.customer = customer
                sale.record_date = datetime.datetime.strptime(record_date, '%d-%m-%Y')
                sale.save()

            return JsonResponse({'status': 'success'})

        if action == 'save':
            Sale.objects.create(**{
                "amount": amount,
                "customer":customer,
                "record_date":datetime.datetime.strptime(record_date, '%d-%m-%Y'),
                "added_by": request.user
            })
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
    

@csrf_exempt
@login_required
def bulk_sales(request):
    if request.method == 'GET':
        template = request.GET.get('template')
        
        Json_data = [['Customer No','Customer Name','Quantity','Price','Record Date','Amount Paid']]
        
        if template == 'sales-payment':
          Json_data = [['Customer No','Customer Name','Record Date','Amount Paid']]
          
        customers = Customer.objects.all()
        if customers:
            for customer in customers:
                if template == 'sales-payment':
                    Json_data.append([customer.customer_no,customer.name,"",""])
                else:
                    Json_data.append([customer.customer_no,customer.name,"","","",""])
        
        data = {
            'Json_data': Json_data,
            'status': 'success'
        }
        # suppliers.delete()
        return JsonResponse(data)
    
    if request.method == 'POST':
        stock_sales = request.POST.get('stock_sales')
        stock_sales = json.loads(stock_sales)
       
        if stock_sales:
            for stock_sale in stock_sales:
                customer_no = stock_sale.get('Customer No',None)
                quantity = stock_sale.get('Quantity',None)
                price = stock_sale.get('Price',None)
                record_date = stock_sale.get('Record Date',None)
                amount_paid = stock_sale.get('Amount Paid',None)
               
                if customer_no and quantity and price and record_date:
                    StockDelivered.objects.create(**{
                        "quantity": quantity,
                        "price": price,
                        "customer":Customer.objects.filter(customer_no=customer_no).first(),
                        "record_date":datetime.datetime.strptime(record_date, '%Y-%m-%d'),
                        "added_by": request.user
                    })
                
                if customer_no and record_date and amount_paid and float(amount_paid) > 0:
                    Sale.objects.create(**{
                        "amount": amount_paid,
                        "customer":Customer.objects.filter(customer_no=customer_no).first(),
                        "record_date":datetime.datetime.strptime(record_date, '%Y-%m-%d'),
                        "added_by": request.user
                    })
            return JsonResponse({'status': 'success'}) 
    
    return JsonResponse({'status': 'failed'})