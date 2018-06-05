from django.urls import path
from suser import views

urlpatterns = [
    path('', views.UserView.as_view(), name='login'),
    path('checkcode/', views.CheckCode),
    path('logout/', views.Logout, name='logout'),
]
