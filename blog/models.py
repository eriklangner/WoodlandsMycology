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

    def __str__(self):
        return self.title
