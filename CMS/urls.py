"""
URL configuration for CMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from users import views as user_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.index, name='index'),
    path('clear-db', user_views.clear_db, name='clear-db'),
    path('users/', include('users.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('customers/', include('customers.urls')),
    path('purchases/', include('purchases.urls')),
    path('sales/', include('sales.urls')),
     path('locations/', include('locations.urls')),
    path('reports/', include('reports.urls')),
]
