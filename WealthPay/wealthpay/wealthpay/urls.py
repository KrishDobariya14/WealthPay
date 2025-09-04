"""
URL configuration for wealthpay project.

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
from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL
    path('admin/', admin.site.urls),
    path('api/transections/',views.transaction_view),
    path('api/signup/',views.signup),
    path('api/login/',views.login),
    path('get-csrf-token/',views.get_csrf_token),
    path('api/transactions/',views.transaction_list),
    path('api/chatbox/',views.chatbox),
]
