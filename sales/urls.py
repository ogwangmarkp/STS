from django.urls import path
from . import views
urlpatterns = [
    path('sales-list/', views.sale_list, name='sales-list'),
    path('new-sale/', views.sale_form, name='new-sale'),
    path('save-sale/', views.save_sale, name='save-sale'),
     path('payment-list/', views.payment_list, name='payment-list'),
    path('new-payment/', views.payment_form, name='new-payment'),
    path('save-payment/', views.save_payment, name='save-payment')
]