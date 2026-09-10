import uuid

from django.db import migrations, models


def populate_request_ids(apps, schema_editor):
    ContactUsMessage = apps.get_model('tak_devs_app', 'ContactUsMessage')
    for message in ContactUsMessage.objects.filter(request_id__isnull=True).iterator():
        message.request_id = uuid.uuid4()
        message.save(update_fields=['request_id'])


class Migration(migrations.Migration):
    dependencies = [
        ('tak_devs_app', '0033_feedback_moderation_and_invitations'),
        ('tak_devs_app', '0033_project_overview_project_problem_project_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactusmessage',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(model_name='contactusmessage', name='request_id', field=models.UUIDField(editable=False, null=True)),
        migrations.RunPython(populate_request_ids, migrations.RunPython.noop),
        migrations.AlterField(model_name='contactusmessage', name='request_id', field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
        migrations.AddField(model_name='contactusmessage', name='is_spam', field=models.BooleanField(db_index=True, default=False)),
        migrations.AddField(model_name='contactusmessage', name='spam_score', field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name='contactusmessage', name='spam_reasons', field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name='contactusmessage', name='source_ip_hash', field=models.CharField(blank=True, db_index=True, max_length=64)),
        migrations.AddField(model_name='contactusmessage', name='submission_fingerprint', field=models.CharField(blank=True, db_index=True, max_length=64)),
        migrations.AddField(model_name='contactusmessage', name='user_agent', field=models.CharField(blank=True, max_length=500)),
        migrations.AddField(model_name='contactusmessage', name='turnstile_verified', field=models.BooleanField(default=False)),
    ]
