# Generated by Django 4.2 on 2023-04-06 03:36

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0004_alter_property_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), geography=True, srid=4326),
        ),
    ]