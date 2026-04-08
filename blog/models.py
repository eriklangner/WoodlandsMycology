from django.db import models
import datetime


# Create your models here.
class MushroomDetail(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField(("Date"), default=datetime.date.today)
    latin_name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='woodlandsmushrooms/images/')
    url = models.URLField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def cover_photo(self):
        return self.photos.first()

    def __str__(self):
        return self.title


class MushroomPhoto(models.Model):
    mushroom = models.ForeignKey(
        MushroomDetail,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(upload_to='woodlandsmushrooms/photos/')
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.mushroom.title} photo {self.pk}'
