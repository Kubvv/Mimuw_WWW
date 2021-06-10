# Generated by Django 3.1.7 on 2021-03-28 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('serverSide', '0009_auto_20210328_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesection',
            name='parentSection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='serverSide.filesection'),
        ),
        migrations.AlterField(
            model_name='filesection',
            name='status',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='serverSide.statussection'),
        ),
        migrations.AlterField(
            model_name='filesection',
            name='statusData',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='serverSide.statusdata'),
        ),
    ]
