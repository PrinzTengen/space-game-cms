"""Keep the upstream migration history when adding project compatibility fixes."""

from importlib import import_module

Migration = import_module(
    "djangocms_stories.migrations.0002_auto_20250618_1556",
).Migration
