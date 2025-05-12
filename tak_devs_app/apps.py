from django.apps import AppConfig


class TakDevsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tak_devs_app'

    def ready(self):
        import tak_devs_app.signals  # Import the signals
