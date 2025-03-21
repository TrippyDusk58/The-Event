"""
URL configuration for Nairobifestival project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from .import views
from .views import logout_view, mpesa_callback, payment_history
from .views import stk_push_request
from .views import register_view, login_view
from .views import buy_ticket

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('speaker-details/', views.speaker_details, name='speaker_details'),
    path('starter-page/', views.starter_page, name='starter_page'),
    path('contact/', views.contact, name='contact'),
    path('customerlist/', views.customerlist, name='customerlist'),
    path('editcustomer/<int:id>/', views.editcustomer, name='editcustomer'),
    path('deletecustomer/<int:id>/', views.deletecustomer, name='deletecustomer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("register/", register_view, name="register"),
    path('stk-push/', stk_push_request, name='stk_push_request'),
    path("buy_ticket/", buy_ticket, name="buy_ticket"),
    path('mpesa-callback/', mpesa_callback, name='mpesa_callback'),
    path('payments/', payment_history, name='payment_history'),


]
