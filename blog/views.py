from django.shortcuts import render, get_object_or_404
from .models import MushroomDetail


# Create your views here.
from django.http import HttpResponse


def all_blogs(request):
    mushrooms_detail = MushroomDetail.objects.all()
    return render(request, 'blog/all_blogs.html', {'mushrooms_detail':mushrooms_detail})

def detail(request, blog_id):
    blog = get_object_or_404(MushroomDetail, pk=blog_id)
    return render(request, 'blog/detail.html',{'blog':blog})

def map_page(request):
    MushroomDetails = MushroomDetail.objects.all()
    return render(request, 'blog/map_page.html', {'MushroomDetails': MushroomDetails})

def about(request):
    return render(request, 'blog/about.html')