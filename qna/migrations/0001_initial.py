# Generated by Django 4.1.1 on 2022-09-20 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'ordering': ['category'],
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.CharField(max_length=1000)),
                ('resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Feedback',
                'verbose_name_plural': 'Feedbacks',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1000, unique=True)),
                ('vote', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('a', 'Available'), ('f', 'Flag'), ('o', 'Onhold'), ('c', 'Closed')], default='a', max_length=20)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('category', models.ManyToManyField(blank=True, related_name='categoryOfQuestion', to='qna.category')),
                ('edit_user', models.ManyToManyField(blank=True, related_name='userWhoEditQuestion', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(default='2', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='userWhoAskQuestion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='qna.category')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
            },
        ),
        migrations.CreateModel(
            name='QuestionStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='qna.question')),
                ('user', models.ForeignKey(default='2', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='userWhoChangeQuestionStatus', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'QuestionStatusHistory',
                'verbose_name_plural': 'QuestionStatusHistorys',
            },
        ),
        migrations.CreateModel(
            name='Qcomment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qcomment', models.CharField(max_length=600)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qna.question')),
                ('user', models.ForeignKey(default='2', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='userWhoCommentOnQuestion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Qcomment',
                'verbose_name_plural': 'Qcomments',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField(default=0)),
                ('category', models.ManyToManyField(blank=True, to='qna.category')),
                ('role', models.ManyToManyField(blank=True, related_name='usersrole', to='qna.role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('vote', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('edit_user', models.ManyToManyField(blank=True, related_name='userWhoEditAnswer', to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qna.question')),
                ('user', models.ForeignKey(default='2', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='userWhoAnswerQuestion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Answer',
                'verbose_name_plural': 'Answers',
                'ordering': ['question', '-vote'],
            },
        ),
        migrations.CreateModel(
            name='Acomment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acomment', models.CharField(max_length=600)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qna.answer')),
                ('user', models.ForeignKey(default='2', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='userWhoCommentonAnswer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Acomment',
                'verbose_name_plural': 'Acomments',
            },
        ),
    ]
