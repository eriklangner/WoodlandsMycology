from django.urls import path
from . import views
from .views import map_page
from .views import about

app_name = 'blog'


urlpatterns = [
    path('', views.all_blogs, name='all_blogs'),
    path("<int:blog_id>/", views.detail, name="detail"),
    path('map/', map_page, name='map_page'),
    path('about/', views.about, name='about'),

]