# Generated by Django 4.0 on 2021-12-30 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploading_data', '0004_alter_sheet_batchnumber_alter_sheet_ticketname'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sheet',
            unique_together={('ticketname', 'batchNumber')},
        ),
    ]
