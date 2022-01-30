# Generated by Django 4.0 on 2021-12-26 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheeturl', models.FilePathField()),
                ('ticketname', models.IntegerField(unique=True)),
                ('MajentoDate', models.DateTimeField()),
                ('UploadedDate', models.DateTimeField(auto_now_add=True)),
                ('Majentoid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='majentoname', to='auth.user')),
                ('Uploaderid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploadername', to='auth.user')),
            ],
        ),
    ]