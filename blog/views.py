import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import MushroomDetail, MushroomPhoto


def all_blogs(request):
    mushrooms_detail = MushroomDetail.objects.all()
    return render(request, 'blog/all_blogs.html', {'mushrooms_detail': mushrooms_detail})


def detail(request, blog_id):
    blog = get_object_or_404(MushroomDetail, pk=blog_id)
    return render(request, 'blog/detail.html', {'blog': blog})


def map_page(request):
    MushroomDetails = MushroomDetail.objects.all()
    return render(request, 'blog/map_page.html', {'MushroomDetails': MushroomDetails})


def about(request):
    return render(request, 'blog/about.html')


@login_required
def new_find(request):
    today = datetime.date.today()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        latin_name = request.POST.get('latin_name', '').strip()
        description = request.POST.get('description', '').strip()
        date_raw = request.POST.get('date')
        photos = request.FILES.getlist('photos')

        if not title or not latin_name:
            messages.error(request, 'Title and Latin name are required.')
            return render(request, 'blog/new_find.html', {'today': today})

        if not photos:
            messages.error(request, 'Please add at least one photo.')
            return render(request, 'blog/new_find.html', {'today': today})

        try:
            if date_raw:
                find_date = datetime.datetime.strptime(date_raw, '%Y-%m-%d').date()
            else:
                find_date = today
        except ValueError:
            find_date = today

        for f in photos:
            f.seek(0)

        mushroom = MushroomDetail.objects.create(
            title=title,
            latin_name=latin_name,
            description=description,
            date=find_date,
            image=photos[0],
        )

        for i, f in enumerate(photos):
            f.seek(0)
            MushroomPhoto.objects.create(
                mushroom=mushroom,
                image=f,
                order=i,
            )

        messages.success(request, 'Mushroom find saved.')
        return redirect('blog:detail', blog_id=mushroom.pk)

    return render(request, 'blog/new_find.html', {'today': today})
