"""DjangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from submit import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home),
    path('user_img/', views.user_img),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),

    # path('table_data/', views.table_data),
    path('get_connecting_alert/', views.get_connecting_alert),
    path('connect_public_database/', views.connect_public_database),
    path('connect_server_database/', views.connect_server_database),

    path('get_step/', views.get_step),
    path('upload/', views.upload),
    path('generate/', views.generate),
    path('start/', views.start),
    path('area1/', views.area1),
    path('area2/', views.area2),
    path('area3/', views.area3),
    path('area4/', views.area4),
    path('polling/', views.polling),
    path('bug_detail/', views.bug_detail),
    path('dynamic_bug_detail/', views.dynamic_bug_detail),
    path('pause_detection/', views.pause_detection),
    path('continue_detection/', views.continue_detection),
    path('stop_detection/', views.stop_detection),
    path('retest/', views.retest),
    path('review/', views.review),
    path('detection_status/', views.detection_status),
]
