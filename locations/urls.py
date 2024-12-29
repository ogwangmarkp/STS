from django.urls import path
from . import views
urlpatterns = [
    path('location-list/', views.location_list, name='location-list'),
    path('new-location/', views.location_form, name='new-locationr'),
    path('save-location/', views.save_location, name='save-location')
]