# Generated by Django 3.0.3 on 2020-05-01 19:05

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('build_finder', '0006_auto_20200216_1143'),
    ]

    operations = [
#        migrations.AlterField(
#            model_name='cards',
#            name='card_color',
#            field=models.CharField(max_length=20, null=True),
#        ),
#        migrations.AlterField(
#            model_name='cards',
#            name='card_power',
#            field=models.IntegerField(default=0, null=True),
#        ),
#        migrations.AlterField(
#            model_name='cards',
#            name='card_shield',
#            field=models.IntegerField(null=True),
#        ),
#        migrations.AlterField(
#            model_name='cards',
#            name='card_text',
#            field=models.CharField(max_length=256, null=True),
#        ),
#        migrations.AlterField(
#            model_name='cards',
#            name='card_toughness',
#            field=models.IntegerField(null=True),
#        ),
#        migrations.AlterField(
#            model_name='deck',
#            name='create_date',
#            field=models.DateTimeField(default=datetime.datetime(2020, 5, 1, 19, 5, 51, 949271, tzinfo=utc)),
#        ),
        migrations.CreateModel(
            name='Combo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_by', models.CharField(max_length=50)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2020, 5, 1, 19, 5, 51, 950565, tzinfo=utc))),
                ('combo_description', models.CharField(max_length=500)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_finder_combo_card', to='build_finder.Cards')),
                ('combo_card1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_finder_combo_card1', to='build_finder.Cards')),
                ('combo_card2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_finder_combo_card2', to='build_finder.Cards')),
                ('combo_card3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_finder_combo_card3', to='build_finder.Cards')),
            ],
        ),
    ]