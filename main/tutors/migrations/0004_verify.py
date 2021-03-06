# Generated by Django 3.0.4 on 2020-04-15 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutors', '0003_auto_20200414_1731'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnic_front', models.ImageField(upload_to='')),
                ('cnic_back', models.ImageField(upload_to='')),
                ('highist_qual', models.ImageField(upload_to='')),
                ('tutor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tutors.Tutor')),
            ],
        ),
    ]
