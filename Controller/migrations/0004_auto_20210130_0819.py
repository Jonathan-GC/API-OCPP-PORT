# Generated by Django 3.1.5 on 2021-01-30 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Controller', '0003_auto_20210130_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='type_transaction',
            field=models.BooleanField(default=True, verbose_name='Saliente o Entrante'),
        ),
    ]