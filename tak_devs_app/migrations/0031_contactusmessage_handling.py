from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tak_devs_app', '0030_alter_teammember_options_teammember_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactusmessage',
            name='handled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contactusmessage',
            name='handled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_contact_messages', to=settings.AUTH_USER_MODEL),
        ),
    ]
