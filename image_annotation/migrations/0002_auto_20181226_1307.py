# Generated by Django 2.1.4 on 2018-12-26 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_annotation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(to='image_annotation.Group'),
        ),
    ]
