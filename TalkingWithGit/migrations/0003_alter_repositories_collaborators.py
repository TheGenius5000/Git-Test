# Generated by Django 5.0.1 on 2024-02-06 23:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TalkingWithGit', '0002_alter_repositories_directory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='repositories',
            name='collaborators',
            field=models.ManyToManyField(blank=True, related_name='repositories_collaborators', to=settings.AUTH_USER_MODEL),
        ),
    ]