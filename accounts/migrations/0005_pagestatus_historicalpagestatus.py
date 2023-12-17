# Generated by Django 4.2.7 on 2023-12-17 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_lifecycle.mixins
import model_utils.fields
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('accounts', '0004_alter_customuser_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='modified'
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('processing', 'Распознавание'),
                            ('redy', 'Распознано'),
                            ('in_progress', 'Вычитка'),
                            ('formatting', 'Форматирование'),
                            ('check', 'Проверка'),
                            ('done', 'Завершено'),
                        ],
                        default='processing',
                        max_length=100,
                        verbose_name='Статус',
                    ),
                ),
                (
                    'permission_groups',
                    models.ManyToManyField(
                        related_name='page_statuses', to='auth.group', verbose_name='Группы доступа'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Статус страницы',
                'verbose_name_plural': 'Статусы страниц',
                'db_table': '"book"."page_status"',
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPageStatus',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='modified'
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('processing', 'Распознавание'),
                            ('redy', 'Распознано'),
                            ('in_progress', 'Вычитка'),
                            ('formatting', 'Форматирование'),
                            ('check', 'Проверка'),
                            ('done', 'Завершено'),
                        ],
                        default='processing',
                        max_length=100,
                        verbose_name='Статус',
                    ),
                ),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                (
                    'history_type',
                    models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1),
                ),
                (
                    'history_user',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'historical Статус страницы',
                'verbose_name_plural': 'historical Статусы страниц',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
