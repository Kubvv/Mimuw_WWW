# Generated by Django 3.1.7 on 2021-03-28 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('serverSide', '0011_auto_20210328_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesection',
            name='parentFile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='serverSide.file'),
        ),
    ]
