# Generated by Django 3.0.8 on 2020-10-28 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deep', '0002_deep_processed_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deep',
            name='processed_file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
