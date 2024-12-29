from django.urls import path
from . import views
urlpatterns = [
    path('stock-list/', views.stock_list, name='stock-list'),
    path('new-stock/', views.stock_form, name='new-stock'),
    path('save-stock/', views.save_stock, name='save-stock'),
    path('payment-list/', views.payment_list, name='payment-list'),
    path('new-payment/', views.payment_form, name='new-payment'),
    path('save-payment/', views.save_payment, name='save-payment'),
    path('bulk-stocking/', views.bulk_stocking, name='bulk-stocking')
]