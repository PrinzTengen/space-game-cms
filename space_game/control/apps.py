from django.apps import AppConfig


class ControlConfig(AppConfig):
    name = "space_game.control"
    verbose_name = "Management & MCP"

    def ready(self):
        from space_game.control import signals  # noqa: F401, PLC0415
