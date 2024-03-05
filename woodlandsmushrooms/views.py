from django.shortcuts import render
from .models import Mushroom


# Create your views here.

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the woodlandsmushrooms index.")

def home(request):
    mushrooms = Mushroom.objects.all()
    return render(request, 'woodlandsmushrooms/home.html', {'mushrooms':mushrooms})

