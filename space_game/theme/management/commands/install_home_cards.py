"""Replace the old template cards with versioned frontend components."""

from space_game.theme.cards import add_default_cards
from space_game.theme.management.commands.install_home_hero import (
    Command as HeroCommand,
)


class Command(HeroCommand):
    help = "Install the frontend card module and its three initial cards."
    slot = "discovery"
    label = "Cards"
    installer = staticmethod(add_default_cards)
