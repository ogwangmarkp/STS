from django.urls import path
from . import views
urlpatterns = [
    path('weekly-reports/', views.weekly_reports, name='weekly-reports')
]