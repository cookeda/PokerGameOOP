"""
Pytest fixtures and test utilities for poker game tests.
"""
import pytest
from src.core.Card import Card, Rank, Suit
from src.core.Deck import Deck
from src.core.Player import Player
from src.core.Table import Table
from src.core.Pot import Pot
from src.core.Dealer import Dealer
from src.core.GameState import GameState, Phase
from src.core.Action import Action, ActionType


@pytest.fixture
def mock_player():
    """Create a mock player for testing."""
    return Player("TestPlayer", 100, is_human=False)


@pytest.fixture
def mock_players():
    """Create multiple mock players for testing."""
    return [
        Player("Player1", 100, is_human=False),
        Player("Player2", 100, is_human=False),
        Player("Player3", 100, is_human=False),
    ]


@pytest.fixture
def test_table():
    """Create a test table with default settings."""
    return Table(n_seats=6, small_blind=1, big_blind=2)


@pytest.fixture
def test_table_with_players(test_table, mock_players):
    """Create a test table with players already added."""
    for i, player in enumerate(mock_players):
        test_table.add_player(player, seat_index=i)
    return test_table


@pytest.fixture
def test_deck():
    """Create a test deck with a fixed seed for reproducibility."""
    return Deck(seed=42)


@pytest.fixture
def test_pot():
    """Create a test pot."""
    return Pot()


@pytest.fixture
def test_dealer(test_table, test_deck):
    """Create a test dealer."""
    return Dealer(test_table, test_deck)


@pytest.fixture
def test_game_state(test_table_with_players, test_pot):
    """Create a test game state."""
    return GameState(test_table_with_players, test_pot)


class MockAIPlayer(Player):
    """Mock AI player that returns predetermined actions."""
    
    def __init__(self, name, stack, actions=None):
        super().__init__(name, stack, is_human=False)
        self.actions = actions or []
        self.action_index = 0
    
    def get_action(self, game_state):
        """Return the next predetermined action."""
        if self.action_index < len(self.actions):
            action = self.actions[self.action_index]
            self.action_index += 1
            return action
        # Default to fold if no more actions
        from src.core.Action import Action, ActionType
        return Action(self, ActionType.FOLD)


def create_test_table(players_data=None, n_seats=6, small_blind=1, big_blind=2):
    """
    Helper to create table with specified players.
    players_data: list of tuples (name, stack) or None
    """
    table = Table(n_seats=n_seats, small_blind=small_blind, big_blind=big_blind)
    if players_data:
        for i, (name, stack) in enumerate(players_data):
            player = Player(name, stack, is_human=False)
            table.add_player(player, seat_index=i)
    return table


def create_test_players(count=3, stack=100):
    """Helper to create test players with specified stack."""
    return [Player(f"Player{i+1}", stack, is_human=False) for i in range(count)]


def create_test_game_state(table, pot=None, phase=Phase.PRE_FLOP):
    """Helper to create GameState in specific phase."""
    if pot is None:
        pot = Pot()
    game_state = GameState(table, pot)
    # Manually set phase if needed (since constructor always starts PRE_FLOP)
    if phase != Phase.PRE_FLOP:
        game_state.phase = phase
        # Adjust to_act_index for post-flop
        if phase in [Phase.FLOP, Phase.TURN, Phase.RIVER]:
            game_state.to_act_index = (table.dealer_button + 1) % len(table.seats)
    return game_state


def mock_deck_with_order(card_order):
    """
    Helper to create deck with known card order for deterministic tests.
    card_order: list of (rank, suit) tuples
    """
    deck = Deck(seed=None)
    # Reverse the order since we'll pop from the end
    deck.cards = [Card(Rank(rank), Suit(suit)) for rank, suit in reversed(card_order)]
    return deck

