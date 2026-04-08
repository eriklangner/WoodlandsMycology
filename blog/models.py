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
    latitude = models.FloatField(null=True, blank=True, default=0)
    longitude = models.FloatField(null=True, blank=True, default=0)

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

    @staticmethod
    def _convert_to_degrees(value):
        d, m, s = value
        return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)

    def _gps_coords_from_image_path(self, path):
        try:
            from PIL import Image
            from PIL.ExifTags import GPSTAGS

            img = Image.open(path)
            gps_data = None

            try:
                exif = img.getexif()
                if exif is not None:
                    gps_ifd = exif.get_ifd(0x8825)
                    if gps_ifd:
                        gps_data = {GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}
            except Exception:
                gps_data = None

            if not gps_data:
                try:
                    exif = img._getexif()
                    if exif:
                        gps_info = exif.get(34853)
                        if gps_info:
                            gps_data = {GPSTAGS.get(k, k): v for k, v in gps_info.items()}
                except Exception:
                    gps_data = None

            if not gps_data:
                return None

            lat = gps_data.get('GPSLatitude')
            lat_ref = gps_data.get('GPSLatitudeRef')
            lon = gps_data.get('GPSLongitude')
            lon_ref = gps_data.get('GPSLongitudeRef')

            if lat is None or lon is None:
                return None

            lat_deg = self._convert_to_degrees(lat)
            if isinstance(lat_ref, bytes):
                lat_ref = lat_ref.decode('ascii', errors='replace')
            if lat_ref != 'N':
                lat_deg = -lat_deg

            lon_deg = self._convert_to_degrees(lon)
            if isinstance(lon_ref, bytes):
                lon_ref = lon_ref.decode('ascii', errors='replace')
            if lon_ref != 'E':
                lon_deg = -lon_deg

            return (lat_deg, lon_deg)
        except Exception:
            return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            if not self.image:
                return
            mushroom = self.mushroom
            needs_fill = (
                (mushroom.latitude is None or mushroom.latitude == 0)
                and (mushroom.longitude is None or mushroom.longitude == 0)
            )
            if not needs_fill:
                return
            coords = self._gps_coords_from_image_path(self.image.path)
            if coords is None:
                return
            lat_deg, lon_deg = coords
            mushroom.latitude = lat_deg
            mushroom.longitude = lon_deg
            mushroom.save(update_fields=['latitude', 'longitude'])
        except Exception:
            pass

    def __str__(self):
        return f'{self.mushroom.title} photo {self.pk}'
