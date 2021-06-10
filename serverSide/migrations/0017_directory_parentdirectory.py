# Generated by Django 3.1.7 on 2021-03-29 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('serverSide', '0016_auto_20210328_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='directory',
            name='parentDirectory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='serverSide.directory'),
        ),
    ]