# Generated by Django 2.1.4 on 2020-04-09 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_gene_symbols'),
    ]

    operations = [
        migrations.AddField(
            model_name='gene',
            name='ensembl_id',
            field=models.IntegerField(default=-1),
        ),
    ]
