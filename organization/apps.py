from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    name = "organization"

    # Import signals
    def ready(self):
        import organization.signals
