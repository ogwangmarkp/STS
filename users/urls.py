from django.urls import path
from . import views
urlpatterns = [
    
    
    path('login/', views.login_user, name='login'),
    path('logout-user', views.logout_user, name="logout-user"), 
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('user-list/', views.user_list, name='user-list'),
]