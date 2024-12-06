from django.urls import path
from . import views
urlpatterns = [
    path('supplier-list/', views.supplier_list, name='suppliers-list'),
    path('new-supplier/', views.supplier_form, name='new-supplier'),
    path('save-supplier/', views.save_supplier, name='save-supplier')
]