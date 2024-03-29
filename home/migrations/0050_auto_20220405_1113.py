# Generated by Django 3.2.9 on 2022-04-05 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0049_auto_20220405_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='enhancer',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.track'),
        ),
        migrations.AddField(
            model_name='variant',
            name='build',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.build'),
        ),
        migrations.AddField(
            model_name='variant',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.track'),
        ),
    ]
