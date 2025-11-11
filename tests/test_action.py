"""
Tests for Action system (ActionType enum and Action class).
"""
import pytest
from src.core.Action import Action, ActionType
from src.core.Player import Player


class TestActionType:
    """Tests for ActionType enum."""
    
    def test_all_enum_values_exist(self):
        """Test all enum values exist."""
        assert ActionType.FOLD
        assert ActionType.CHECK
        assert ActionType.CALL
        assert ActionType.BET
        assert ActionType.RAISE
        assert ActionType.ALL_IN
    
    def test_enum_value_strings(self):
        """Test enum value strings are correct."""
        assert ActionType.FOLD.value == "fold"
        assert ActionType.CHECK.value == "check"
        assert ActionType.CALL.value == "call"
        assert ActionType.BET.value == "bet"
        assert ActionType.RAISE.value == "raise"
        assert ActionType.ALL_IN.value == "all_in"


class TestAction:
    """Tests for Action class."""
    
    @pytest.fixture
    def test_player(self):
        """Create a test player."""
        return Player("TestPlayer", 100)
    
    def test_action_creation_fold(self, test_player):
        """Test creating a fold action."""
        action = Action(test_player, ActionType.FOLD)
        assert action.player == test_player
        assert action.type == ActionType.FOLD
        assert action.amount == 0
    
    def test_action_creation_check(self, test_player):
        """Test creating a check action."""
        action = Action(test_player, ActionType.CHECK)
        assert action.player == test_player
        assert action.type == ActionType.CHECK
        assert action.amount == 0
    
    def test_action_creation_call(self, test_player):
        """Test creating a call action."""
        action = Action(test_player, ActionType.CALL, 50)
        assert action.player == test_player
        assert action.type == ActionType.CALL
        assert action.amount == 50
    
    def test_action_creation_bet(self, test_player):
        """Test creating a bet action."""
        action = Action(test_player, ActionType.BET, 25)
        assert action.player == test_player
        assert action.type == ActionType.BET
        assert action.amount == 25
    
    def test_action_creation_raise(self, test_player):
        """Test creating a raise action."""
        action = Action(test_player, ActionType.RAISE, 100)
        assert action.player == test_player
        assert action.type == ActionType.RAISE
        assert action.amount == 100
    
    def test_action_creation_all_in(self, test_player):
        """Test creating an all-in action."""
        action = Action(test_player, ActionType.ALL_IN, 100)
        assert action.player == test_player
        assert action.type == ActionType.ALL_IN
        assert action.amount == 100
    
    def test_action_string_representation_fold(self, test_player):
        """Test string representation for fold."""
        action = Action(test_player, ActionType.FOLD)
        assert str(action) == "TestPlayer folds"
    
    def test_action_string_representation_check(self, test_player):
        """Test string representation for check."""
        action = Action(test_player, ActionType.CHECK)
        assert str(action) == "TestPlayer checks"
    
    def test_action_string_representation_call(self, test_player):
        """Test string representation for call."""
        action = Action(test_player, ActionType.CALL, 50)
        assert str(action) == "TestPlayer calls 50"
    
    def test_action_string_representation_bet(self, test_player):
        """Test string representation for bet."""
        action = Action(test_player, ActionType.BET, 25)
        assert str(action) == "TestPlayer bets 25"
    
    def test_action_string_representation_raise(self, test_player):
        """Test string representation for raise."""
        action = Action(test_player, ActionType.RAISE, 100)
        assert str(action) == "TestPlayer raises to 100"
    
    def test_action_string_representation_all_in(self, test_player):
        """Test string representation for all-in."""
        action = Action(test_player, ActionType.ALL_IN, 100)
        assert str(action) == "TestPlayer goes all-in with 100"
    
    def test_action_repr(self, test_player):
        """Test repr representation."""
        action = Action(test_player, ActionType.BET, 50)
        repr_str = repr(action)
        assert "TestPlayer" in repr_str
        assert "bet" in repr_str
        assert "50" in repr_str
    
    def test_action_with_zero_amount(self, test_player):
        """Test actions that don't need amounts work correctly."""
        fold_action = Action(test_player, ActionType.FOLD)
        check_action = Action(test_player, ActionType.CHECK)
        
        assert fold_action.amount == 0
        assert check_action.amount == 0
    
    def test_action_with_amount(self, test_player):
        """Test bet/raise/call actions store amounts correctly."""
        bet_action = Action(test_player, ActionType.BET, 25)
        raise_action = Action(test_player, ActionType.RAISE, 50)
        call_action = Action(test_player, ActionType.CALL, 30)
        
        assert bet_action.amount == 25
        assert raise_action.amount == 50
        assert call_action.amount == 30

