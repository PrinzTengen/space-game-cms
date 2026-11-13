"""Replace the homepage include with the native Stories plugin."""

from space_game.theme.management.commands.install_home_hero import (
    Command as HeroCommand,
)
from space_game.theme.stories import add_default_latest_posts


class Command(HeroCommand):
    help = "Install djangocms-stories latest entries on existing homepages."
    slot = "latest"
    label = "Stories"
    installer = staticmethod(add_default_latest_posts)
