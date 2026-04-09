from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_mushroomdetail_ai_identification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mushroomdetail',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='woodlandsmushrooms/images/'),
        ),
    ]
