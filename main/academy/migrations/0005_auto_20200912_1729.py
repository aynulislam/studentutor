# Generated by Django 3.0.4 on 2020-09-12 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0004_invitations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitations',
            old_name='student_ad',
            new_name='tutor_ad',
        ),
    ]
