# Generated by Django 2.1.5 on 2022-02-02 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('single', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='comments_text',
            field=models.CharField(blank=True, default='', max_length=600),
        ),
        migrations.AlterField(
            model_name='case',
            name='coordinates_text',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='case',
            name='email_text',
            field=models.CharField(max_length=62),
        ),
        migrations.AlterField(
            model_name='case',
            name='name_text',
            field=models.CharField(max_length=90),
        ),
        migrations.AlterField(
            model_name='case',
            name='phenotypes_text',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]