# Generated by Django 2.2.5 on 2020-02-13 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('build_finder', '0003_auto_20200213_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deck',
            name='deck_PW',
            field=models.CharField(default='All', max_length=100),
        ),
    ]