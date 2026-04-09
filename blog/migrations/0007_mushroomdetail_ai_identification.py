from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_mushroomdetail_nullable_coords'),
    ]

    operations = [
        migrations.AddField(
            model_name='mushroomdetail',
            name='ai_identification',
            field=models.TextField(blank=True, default=''),
        ),
    ]
