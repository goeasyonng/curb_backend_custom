# Generated by Django 4.2 on 2023-04-29 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Auth_sms",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "phone_number",
                    models.CharField(
                        max_length=11,
                        primary_key=True,
                        serialize=False,
                        verbose_name="휴대폰 번호",
                    ),
                ),
                ("auth_number", models.IntegerField(verbose_name="인증 번호")),
            ],
            options={
                "db_table": "auth",
            },
        ),
    ]
