# Generated by Django 3.1.7 on 2021-03-28 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serverSide', '0014_auto_20210328_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesection',
            name='lastUpdated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='sectioncategory',
            name='lastUpdated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
