"""Replace the old template gallery with versioned frontend components."""

from space_game.theme.gallery import add_default_gallery
from space_game.theme.management.commands.install_home_hero import (
    Command as HeroCommand,
)


class Command(HeroCommand):
    help = "Install the frontend gallery and its two initial images."
    slot = "gallery"
    label = "Gallery"
    installer = staticmethod(add_default_gallery)
