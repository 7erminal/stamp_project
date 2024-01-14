from django.urls import path, include
from .views import index
from .views import upload

urlpatterns = [
    path('', index, name='home'),
    path('upload/', upload, name='upload'),
]