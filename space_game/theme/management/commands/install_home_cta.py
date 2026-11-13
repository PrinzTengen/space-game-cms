"""Replace the old community callout with a versioned frontend component."""

from space_game.theme.cta import add_default_cta
from space_game.theme.management.commands.install_home_hero import (
    Command as HeroCommand,
)


class Command(HeroCommand):
    help = "Install the frontend CTA on existing landing homepages."
    slot = "community"
    label = "CTA"
    installer = staticmethod(add_default_cta)
