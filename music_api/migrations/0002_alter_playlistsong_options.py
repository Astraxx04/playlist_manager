# Generated by Django 5.0.4 on 2024-05-04 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='playlistsong',
            options={'ordering': ['position']},
        ),
    ]
