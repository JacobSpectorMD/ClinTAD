# Generated by Django 2.1.4 on 2018-12-21 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_auto_20181220_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hpo',
            name='comment',
            field=models.CharField(default='', max_length=1600),
        ),
        migrations.AlterField(
            model_name='hpo',
            name='definition',
            field=models.CharField(default='', max_length=1600),
        ),
    ]
