from django.apps import AppConfig


class NasrulhifzConfig(AppConfig):
    name = 'nasrulhifz'

    def ready(self):
        import nasrulhifz.signals  # noqa
