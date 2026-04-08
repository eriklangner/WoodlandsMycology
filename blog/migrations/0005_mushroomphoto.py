# Generated manually for MushroomPhoto

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_mushroomdetail_latitude_mushroomdetail_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='MushroomPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='woodlandsmushrooms/photos/')),
                ('caption', models.CharField(blank=True, max_length=300)),
                ('order', models.PositiveIntegerField(default=0)),
                ('mushroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='blog.mushroomdetail')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]
