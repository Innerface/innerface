"""chatbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls.static import static
from sdisplay import views
from chatbot import views as chatbot_view
from chatbot import settings

urlpatterns = [
    path('admin/', include('data_admin.urls')),
    path('', include('sdisplay.urls')),
    path('user/', include('suser.urls')),
    path('home/', chatbot_view.home),
    path('ask/', chatbot_view.ask),
    path('test/', chatbot_view.test_redis),
    path('weixin', chatbot_view.check_signature),
    path('robot/ask/', chatbot_view.robot_ask),
]

# if settings.DEBUG is False:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
