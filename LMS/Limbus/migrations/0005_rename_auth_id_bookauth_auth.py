# Generated by Django 4.1.3 on 2023-04-27 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Limbus', '0004_alter_returnedbooks_returned'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookauth',
            old_name='auth_id',
            new_name='auth',
        ),
    ]
