from django.urls import path
from .views import test_list

urlpatterns = [
    path('', test_list, name='test_list'),

]