from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'
    verbose_name = 'Tickets'
    
    def ready(self):
        """Register signal handlers when app is ready."""
        import tickets.signals  # noqa: F401
