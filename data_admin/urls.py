from django.urls import path
from data_admin import views

urlpatterns = [
    path('synonyms', views.SynonymsView.as_view(), name='synonyms'),
    path('emotional', views.EmotionalView.as_view(), name='emotional'),
    path('sensitive', views.SensitiveView.as_view(), name='sensitive'),
    path('sensitive_init/', views.sensitive_init, name='sensitive_init'),
    path('synonyms_init/', views.synonyms_init, name='synonyms_init'),
    path('synonyms_file_update/', views.synonyms_file_update, name='synonyms_file_update'),
    path('test/', views.test, name='synonyms_init'),
]
