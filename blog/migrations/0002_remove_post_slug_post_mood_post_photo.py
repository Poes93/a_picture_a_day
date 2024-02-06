# Generated by Django 4.1 on 2024-02-06 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='slug',
        ),
        migrations.AddField(
            model_name='post',
            name='mood',
            field=models.CharField(choices=[('😊', 'Happy 😊'), ('😢', 'Sad 😢'), ('🤩', 'Excited 🤩'), ('😠', 'Angry 😠'), ('❤️', 'Love ❤️')], default='😊', max_length=50),
        ),
        migrations.AddField(
            model_name='post',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='post_photos/'),
        ),
    ]
