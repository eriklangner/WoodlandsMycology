# Generated for Django 4.2 — nullable GPS on MushroomDetail

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_mushroomphoto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mushroomdetail',
            name='latitude',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='mushroomdetail',
            name='longitude',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
