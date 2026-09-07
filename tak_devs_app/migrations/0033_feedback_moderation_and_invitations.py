import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tak_devs_app', '0033_project_overview_project_problem_project_slug_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='projectclient',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='projectclient',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectclient',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='FeedbackInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_name', models.CharField(max_length=100)),
                ('recipient_email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('delivered', 'Delivered'), ('failed', 'Failed'), ('submitted', 'Submitted')], default='pending', max_length=20)),
                ('provider_message_id', models.CharField(blank=True, max_length=255)),
                ('delivery_mode', models.CharField(blank=True, max_length=32)),
                ('last_error', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback_invitations', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_invitations', to='tak_devs_app.project')),
            ],
            options={'ordering': ('-created_at',)},
        ),
        migrations.AddIndex(
            model_name='feedbackinvitation',
            index=models.Index(fields=['status', 'created_at'], name='tak_devs_ap_status_66bf28_idx'),
        ),
    ]
