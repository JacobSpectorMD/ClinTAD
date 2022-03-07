# Generated by Django 2.1.4 on 2018-12-18 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_ut_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.IntegerField(default=-1)),
                ('end', models.IntegerField(default=-1)),
                ('accession', models.CharField(default='', max_length=200)),
                ('study', models.CharField(default='', max_length=200)),
                ('sample_size', models.IntegerField(default=-1)),
                ('chromosome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='home.Chromosome')),
            ],
        ),
    ]
