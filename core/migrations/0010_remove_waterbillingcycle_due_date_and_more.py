# Generated by Django 4.0.3 on 2022-12-01 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_client_slug_alter_waterbillingcycle_month_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waterbillingcycle',
            name='due_date',
        ),
        migrations.RemoveField(
            model_name='waterbillingcycle',
            name='from_date',
        ),
        migrations.RemoveField(
            model_name='waterbillingcycle',
            name='to_date',
        ),
    ]