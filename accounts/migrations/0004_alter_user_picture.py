# Generated by Django 5.1.4 on 2025-01-09 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='picture',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
