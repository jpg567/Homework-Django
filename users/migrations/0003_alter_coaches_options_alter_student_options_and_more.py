# Generated by Django 5.1.6 on 2025-02-18 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_coaches_student'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coaches',
            options={'permissions': [('can_access_coach_endpoint', 'Can access coach endpoint')]},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'permissions': [('can_access_student_endpoint', 'Can access student endpoint')]},
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
