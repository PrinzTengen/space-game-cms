"""Keep the upstream migration history when adding project compatibility fixes."""

from importlib import import_module

Migration = import_module("djangocms_stories.migrations.0001_initial").Migration
