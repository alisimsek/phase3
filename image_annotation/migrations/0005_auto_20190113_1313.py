# Generated by Django 2.1.4 on 2019-01-13 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_annotation', '0004_auto_20190113_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labeledimage',
            name='image',
            field=models.ImageField(height_field='height', upload_to='static/uploaded_images/', width_field='width'),
        ),
    ]
