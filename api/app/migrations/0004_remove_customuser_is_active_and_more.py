# Generated by Django 4.2 on 2023-04-12 17:53

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_staff',
        ),
        migrations.AddField(
            model_name='customuser',
            name='score',
            field=models.FloatField(default=0, validators=[app.models.score_check]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='solved',
            field=models.IntegerField(default=0),
        ),
    ]
