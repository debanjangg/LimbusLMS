# Generated by Django 4.1.3 on 2023-04-13 07:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Authors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=20)),
                ('lastName', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='BookAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Limbus.authors')),
            ],
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=20)),
                ('lastName', models.CharField(max_length=20)),
                ('phone_no', models.CharField(max_length=10)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('memb_since', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Books',
            fields=[
                ('isbn', models.BigIntegerField(primary_key=True, serialize=False, validators=[django.core.validators.MinValueValidator(9780000000000), django.core.validators.MaxValueValidator(9799999999999)])),
                ('bookName', models.CharField(max_length=50)),
                ('pubName', models.CharField(max_length=20)),
                ('inventory', models.IntegerField(default=0)),
                ('authors', models.ManyToManyField(through='Limbus.BookAuth', to='Limbus.authors')),
            ],
        ),
        migrations.AddField(
            model_name='bookauth',
            name='isbn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Limbus.books'),
        ),
        migrations.CreateModel(
            name='BookIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('returned', models.BooleanField(default=False)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Limbus.books')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Limbus.members')),
            ],
            options={
                'unique_together': {('member', 'book')},
            },
        ),
    ]