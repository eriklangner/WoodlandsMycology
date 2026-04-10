from django.shortcuts import render
from django.http import HttpResponse
from blog.models import MushroomDetail


# Create your views here.


def index(request):
        return HttpResponse("Hello, world. You're at the woodlandsmushrooms index.")

def home(request):
        mushrooms = MushroomDetail.objects.all().order_by('-date')
        return render(request, 'woodlandsmushrooms/home.html', {'mushrooms': mushrooms})
