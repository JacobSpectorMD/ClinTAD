# Generated by Django 3.2.16 on 2023-04-03 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0053_auto_20230403_1218'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='track',
            name='doi',
        ),
        migrations.AddField(
            model_name='track',
            name='article_name',
            field=models.CharField(default='', max_length=500),
        ),
    ]
