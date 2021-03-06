# Generated by Django 3.1.7 on 2021-03-27 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serverSide', '0004_auto_20210327_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='availability',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='directory',
            name='validity',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='availability',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='validity',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='filesection',
            name='validity',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='statusdata',
            name='validity',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='statussection',
            name='validity',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='validity',
            field=models.BooleanField(default=True),
        ),
    ]
