from django.urls import path
from . import views
urlpatterns = [
    path('customer-list/', views.customer_list, name='customer-list'),
    path('new-customer/', views.customer_form, name='new-customer'),
    path('save-customer/', views.save_customer, name='save-customer')
]