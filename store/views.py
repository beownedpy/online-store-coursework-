from django.shortcuts import render
from .models import TestModel

def test_list(request):
    items = TestModel.objects.all()
    return render(request, 'test_list.html', {'items': items})