from django.urls import path
from . import views

app_name = 'blog'


urlpatterns = [
    path('', views.all_blogs, name='all_blogs'),
    path('new-find/', views.new_find, name='new_find'),
    path("<int:blog_id>/", views.detail, name="detail"),
    path('map/', views.map_page, name='map_page'),
    path('about/', views.about, name='about'),
]
