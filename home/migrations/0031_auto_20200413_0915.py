# Generated by Django 2.1.4 on 2020-04-13 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_gene_omims'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gene',
            name='omims',
            field=models.ManyToManyField(related_name='genes', to='home.Omim'),
        ),
    ]
