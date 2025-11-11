"""
Tests for Player class (initialization, action methods, state management, decision interface).
"""
import pytest
from unittest.mock import patch, MagicMock
from src.core.Player import Player
from src.core.Action import Action, ActionType
from src.core.Table import Table
from src.core.Pot import Pot
from src.core.GameState import GameState
from tests.conftest import MockAIPlayer


class TestPlayerInitialization:
    """Tests for player initialization."""
    
    def test_basic_creation(self):
        """Create player with name and stack, verify attributes initialized."""
        player = Player("TestPlayer", 100)
        assert player.name == "TestPlayer"
        assert player.stack == 100
        assert player.hand == []
        assert player.current_bet == 0
        assert player.is_active is True
        assert player.has_folded is False
        assert player.is_all_in is False
        assert player.seat_position is None
    
    def test_human_vs_ai_flag(self):
        """Verify is_human flag set correctly."""
        human_player = Player("Human", 100, is_human=True)
        ai_player = Player("AI", 100, is_human=False)
        
        assert human_player.is_human is True
        assert ai_player.is_human is False
    
    def test_initial_state(self):
        """Verify current_bet=0, is_active=True, has_folded=False, is_all_in=False."""
        player = Player("Player", 100)
        assert player.current_bet == 0
        assert player.is_active is True
        assert player.has_folded is False
        assert player.is_all_in is False


class TestPlayerActionMethods:
    """Tests for player action methods."""
    
    @pytest.fixture
    def player(self):
        """Create a test player."""
        return Player("TestPlayer", 100, is_human=False)
    
    def test_post_blind(self, player):
        """Post small/big blind, verify stack decreases, current_bet increases."""
        initial_stack = player.stack
        amount = player.post_blind(5)
        
        assert player.stack == initial_stack - 5
        assert player.current_bet == 5
        assert amount == 5
    
    def test_post_blind_insufficient_chips(self, player):
        """Post blind when stack < amount, verify only posts available chips."""
        player.stack = 3
        amount = player.post_blind(5)
        
        assert player.stack == 0
        assert player.current_bet == 3
        assert amount == 3
    
    def test_bet(self, player):
        """Place bet, verify stack and current_bet update correctly."""
        initial_stack = player.stack
        initial_bet = player.current_bet
        amount = player.bet(25)
        
        assert player.stack == initial_stack - 25
        assert player.current_bet == initial_bet + 25
        assert amount == 25
    
    def test_bet_all_in(self, player):
        """Bet entire stack, verify is_all_in flag set."""
        initial_stack = player.stack
        player.bet(initial_stack)
        
        assert player.stack == 0
        assert player.is_all_in is True
        assert player.current_bet == initial_stack
    
    def test_call(self, player):
        """Call amount, verify stack decreases, current_bet increases."""
        initial_stack = player.stack
        call_amount = player.call(30)
        
        assert player.stack == initial_stack - 30
        assert player.current_bet == 30
        assert call_amount == 30
    
    def test_call_partial(self, player):
        """Call when stack < call amount, verify only calls available chips."""
        player.stack = 20
        call_amount = player.call(30)
        
        assert player.stack == 0
        assert player.current_bet == 20
        assert call_amount == 20
        assert player.is_all_in is True
    
    def test_fold(self, player):
        """Fold hand, verify has_folded=True, is_active=False."""
        player.fold()
        
        assert player.has_folded is True
        assert player.is_active is False
    
    def test_check(self, player):
        """Check action, verify no state changes."""
        initial_stack = player.stack
        initial_bet = player.current_bet
        initial_folded = player.has_folded
        initial_active = player.is_active
        
        player.check()
        
        assert player.stack == initial_stack
        assert player.current_bet == initial_bet
        assert player.has_folded == initial_folded
        assert player.is_active == initial_active
    
    def test_all_in(self, player):
        """Go all-in, verify stack=0, is_all_in=True, current_bet updated."""
        initial_stack = player.stack
        amount = player.all_in()
        
        assert player.stack == 0
        assert player.is_all_in is True
        assert player.current_bet == initial_stack
        assert amount == initial_stack


class TestPlayerStateManagement:
    """Tests for player state management."""
    
    def test_reset_hand_state(self):
        """Reset player after hand, verify all state attributes reset correctly."""
        player = Player("Player", 100)
        player.current_bet = 50
        player.is_active = False
        player.is_all_in = True
        player.has_folded = True
        player.hand = [1, 2]  # Mock cards
        
        player.reset_hand_state()
        
        assert player.current_bet == 0
        assert player.is_active is True
        assert player.is_all_in is False
        assert player.has_folded is False
        assert player.hand == []
    
    def test_seat_position_assignment(self):
        """Verify seat_position set when added to table."""
        player = Player("Player", 100)
        table = Table()
        table.add_player(player, seat_index=3)
        
        assert player.seat_position == 3


class TestPlayerDecisionInterface:
    """Tests for player decision interface."""
    
    def test_decide_action_ai(self):
        """Create AI player subclass, verify get_action() called."""
        ai_player = MockAIPlayer("AIPlayer", 100, [
            Action(None, ActionType.CALL, 10)
        ])
        
        # Mock game state
        mock_game_state = MagicMock()
        action = ai_player.decide_action(mock_game_state)
        
        assert action.type == ActionType.CALL
        assert action.amount == 10
    
    def test_decide_action_ai_not_implemented(self):
        """Test that regular Player raises NotImplementedError for AI."""
        player = Player("Player", 100, is_human=False)
        mock_game_state = MagicMock()
        
        with pytest.raises(NotImplementedError):
            player.decide_action(mock_game_state)
    
    @patch('builtins.input', return_value='fold')
    def test_decide_action_human_fold(self, mock_input):
        """Mock human input for fold, verify correct Action returned."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        
        # Mock the game state to have valid actions
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.FOLD]):
            with patch.object(game_state, 'get_call_amount', return_value=0):
                action = player.decide_action(game_state)
                assert action.type == ActionType.FOLD
    
    @patch('builtins.input', return_value='check')
    def test_decide_action_human_check(self, mock_input):
        """Mock human input for check."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        game_state.current_bet = 0
        
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.CHECK, ActionType.BET]):
            with patch.object(game_state, 'get_call_amount', return_value=0):
                action = player.decide_action(game_state)
                assert action.type == ActionType.CHECK
    
    @patch('builtins.input', return_value='call')
    def test_decide_action_human_call(self, mock_input):
        """Mock human input for call."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        game_state.current_bet = 20
        
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.FOLD, ActionType.CALL]):
            with patch.object(game_state, 'get_call_amount', return_value=20):
                action = player.decide_action(game_state)
                assert action.type == ActionType.CALL
                assert action.amount == 20
    
    @patch('builtins.input', return_value='bet 25')
    def test_decide_action_human_bet(self, mock_input):
        """Mock human input for bet."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        game_state.current_bet = 0
        game_state.min_raise = 2
        
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.CHECK, ActionType.BET]):
            with patch.object(game_state, 'get_call_amount', return_value=0):
                action = player.decide_action(game_state)
                assert action.type == ActionType.BET
                assert action.amount == 25
    
    @patch('builtins.input', return_value='raise 50')
    def test_decide_action_human_raise(self, mock_input):
        """Mock human input for raise."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        game_state.current_bet = 20
        game_state.min_raise = 2
        
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.FOLD, ActionType.CALL, ActionType.RAISE]):
            with patch.object(game_state, 'get_call_amount', return_value=20):
                action = player.decide_action(game_state)
                assert action.type == ActionType.RAISE
                assert action.amount == 50
    
    @patch('builtins.input', return_value='all-in')
    def test_decide_action_human_all_in(self, mock_input):
        """Mock human input for all-in."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.FOLD, ActionType.ALL_IN]):
            with patch.object(game_state, 'get_call_amount', return_value=0):
                action = player.decide_action(game_state)
                assert action.type == ActionType.ALL_IN
                assert action.amount == 100
    
    @patch('builtins.input', side_effect=['invalid', 'fold'])
    def test_invalid_input_handling(self, mock_input):
        """Test error handling for invalid human inputs."""
        player = Player("HumanPlayer", 100, is_human=True)
        table = Table()
        pot = Pot()
        table.add_player(player, seat_index=0)
        game_state = GameState(table, pot)
        
        with patch.object(game_state, 'get_valid_actions', return_value=[ActionType.FOLD]):
            with patch.object(game_state, 'get_call_amount', return_value=0):
                action = player.decide_action(game_state)
                assert action.type == ActionType.FOLD
                assert mock_input.call_count == 2  # Called twice due to invalid input

