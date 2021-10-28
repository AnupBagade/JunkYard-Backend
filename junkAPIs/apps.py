from django.apps import AppConfig


class JunkapisConfig(AppConfig):
    name = 'junkAPIs'

    def ready(self):
        import junkAPIs.receivers