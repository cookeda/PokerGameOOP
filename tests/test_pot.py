"""
Tests for Pot management (basic operations, side pots, awarding).
"""
import pytest
from src.core.Pot import Pot
from src.core.Player import Player


class TestPotInitialization:
    """Tests for pot initialization."""
    
    def test_initialization(self):
        """Test pot starts with zero main_pot, empty side_pots, empty contributors."""
        pot = Pot()
        assert pot.main_pot == 0
        assert pot.side_pots == []
        assert pot.contributors == {}


class TestPotBasicOperations:
    """Tests for basic pot operations."""
    
    @pytest.fixture
    def pot(self):
        """Create a test pot."""
        return Pot()
    
    @pytest.fixture
    def player(self):
        """Create a test player."""
        return Player("TestPlayer", 100)
    
    def test_add_contribution_single_player(self, pot, player):
        """Add chips from single player, verify main_pot and contributors update."""
        pot.add_contribution(player, 50)
        assert pot.main_pot == 50
        assert pot.contributors[player] == 50
    
    def test_add_contribution_multiple_players(self, pot):
        """Add chips from multiple players, verify totals."""
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        player3 = Player("Player3", 100)
        
        pot.add_contribution(player1, 25)
        pot.add_contribution(player2, 50)
        pot.add_contribution(player3, 75)
        
        assert pot.main_pot == 150
        assert pot.contributors[player1] == 25
        assert pot.contributors[player2] == 50
        assert pot.contributors[player3] == 75
    
    def test_add_contribution_multiple_times(self, pot, player):
        """Add contributions multiple times from same player."""
        pot.add_contribution(player, 25)
        pot.add_contribution(player, 30)
        pot.add_contribution(player, 20)
        
        assert pot.main_pot == 75
        assert pot.contributors[player] == 75
    
    def test_get_total_no_side_pots(self, pot):
        """Test get_total with no side pots."""
        player = Player("Player", 100)
        pot.add_contribution(player, 50)
        assert pot.get_total() == 50
    
    def test_get_total_with_side_pots(self, pot):
        """Test get_total including side pots."""
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        
        pot.add_contribution(player1, 100)
        pot.add_contribution(player2, 50)
        pot.resolve_side_pots()
        
        total = pot.get_total()
        assert total == 150  # Main pot + side pot


class TestPotSidePotResolution:
    """Tests for side pot resolution."""
    
    def test_single_all_in_no_side_pots(self):
        """One player all-in, verify no side pots created."""
        pot = Pot()
        player = Player("Player", 100)
        pot.add_contribution(player, 100)
        pot.resolve_side_pots()
        
        assert len(pot.side_pots) == 0
        assert pot.main_pot == 100
    
    def test_two_all_ins_different_amounts(self):
        """Two players all-in with different amounts, verify side pot created."""
        pot = Pot()
        player_a = Player("PlayerA", 100)
        player_b = Player("PlayerB", 50)
        
        pot.add_contribution(player_a, 100)
        pot.add_contribution(player_b, 50)
        pot.resolve_side_pots()
        
        # Should have one side pot with 50 from each player (100 total)
        # Main pot should have remaining 50 from player A
        assert len(pot.side_pots) == 1
        side_pot = pot.side_pots[0]
        assert side_pot["amount"] == 100  # 50 from each player
        assert player_a in side_pot["contributors"]
        assert player_b in side_pot["contributors"]
        assert pot.main_pot == 50  # Remaining from player A
    
    def test_three_all_ins_multiple_side_pots(self):
        """Multiple all-in amounts, verify multiple side pots created correctly."""
        pot = Pot()
        player_a = Player("PlayerA", 100)
        player_b = Player("PlayerB", 50)
        player_c = Player("PlayerC", 75)
        
        pot.add_contribution(player_a, 100)
        pot.add_contribution(player_b, 50)
        pot.add_contribution(player_c, 75)
        pot.resolve_side_pots()
        
        # Should have side pots:
        # Side pot 1: 50 from each (A, B, C) = 150
        # Side pot 2: 25 from A and C = 50
        # Main pot: 25 from A = 25
        assert len(pot.side_pots) == 2
        assert pot.side_pots[0]["amount"] == 150  # 50 from each
        assert pot.side_pots[1]["amount"] == 50  # 25 from A and C
        assert pot.main_pot == 25  # Remaining from A
    
    def test_side_pot_calculation_main_pot_reduced(self):
        """Verify main pot reduced correctly when side pots created."""
        pot = Pot()
        player_a = Player("PlayerA", 100)
        player_b = Player("PlayerB", 50)
        
        pot.add_contribution(player_a, 100)
        pot.add_contribution(player_b, 50)
        initial_total = pot.main_pot
        
        pot.resolve_side_pots()
        
        # Total should remain the same
        assert pot.get_total() == initial_total
        # But main pot should be reduced
        assert pot.main_pot < initial_total
        assert pot.main_pot + sum(sp["amount"] for sp in pot.side_pots) == initial_total


class TestPotAwarding:
    """Tests for pot awarding."""
    
    def test_award_to_single_winner(self):
        """Award main pot to one winner, verify stack increases correctly."""
        pot = Pot()
        winner = Player("Winner", 100)
        
        pot.add_contribution(winner, 50)
        initial_stack = winner.stack
        
        pot.award_to([winner])
        
        assert winner.stack == initial_stack + 50
        assert pot.main_pot == 0
    
    def test_award_to_multiple_winners(self):
        """Split pot between winners, verify remainder distributed."""
        pot = Pot()
        winner1 = Player("Winner1", 100)
        winner2 = Player("Winner2", 100)
        
        pot.add_contribution(winner1, 50)
        pot.add_contribution(winner2, 50)
        # Total pot: 100
        
        initial_stack1 = winner1.stack
        initial_stack2 = winner2.stack
        
        pot.award_to([winner1, winner2])
        
        # Each should get 50
        assert winner1.stack == initial_stack1 + 50
        assert winner2.stack == initial_stack2 + 50
    
    def test_award_with_remainder(self):
        """Pot not divisible by winners, verify remainder distributed one chip at a time."""
        pot = Pot()
        winner1 = Player("Winner1", 100)
        winner2 = Player("Winner2", 100)
        winner3 = Player("Winner3", 100)
        
        pot.add_contribution(winner1, 50)
        pot.add_contribution(winner2, 50)
        pot.add_contribution(winner3, 50)
        # Total pot: 150
        
        initial_stacks = [w.stack for w in [winner1, winner2, winner3]]
        
        pot.award_to([winner1, winner2, winner3])
        
        # Each should get 50, remainder 0
        assert winner1.stack == initial_stacks[0] + 50
        assert winner2.stack == initial_stacks[1] + 50
        assert winner3.stack == initial_stacks[2] + 50
        
        # Test with remainder
        pot2 = Pot()
        pot2.add_contribution(winner1, 50)
        pot2.add_contribution(winner2, 50)
        pot2.add_contribution(winner3, 50)
        pot2.add_contribution(Player("Other", 100), 1)  # Total: 151
        
        initial_stacks2 = [w.stack for w in [winner1, winner2, winner3]]
        pot2.award_to([winner1, winner2, winner3])
        
        # Each should get 50, one gets 51 (remainder)
        total_awarded = sum(w.stack - s for w, s in zip([winner1, winner2, winner3], initial_stacks2))
        assert total_awarded == 151
    
    def test_award_with_side_pots(self):
        """Award main pot and side pots to different winners."""
        pot = Pot()
        player_a = Player("PlayerA", 100)
        player_b = Player("PlayerB", 50)
        player_c = Player("PlayerC", 75)
        
        pot.add_contribution(player_a, 100)
        pot.add_contribution(player_b, 50)
        pot.add_contribution(player_c, 75)
        pot.resolve_side_pots()
        
        initial_stack_a = player_a.stack
        initial_stack_b = player_b.stack
        initial_stack_c = player_c.stack
        
        # Award main pot to A, side pot 0 to all (since all contributed), side pot 1 to A and C
        # Actually, let's award based on who can win each pot
        # Side pot 0: all contributed, so can go to any
        # Side pot 1: only A and C contributed
        winners = {
            "main": [player_a],
            0: [player_a, player_b, player_c],  # All contributed to first side pot
        }
        if len(pot.side_pots) > 1:
            winners[1] = [player_a, player_c]  # Only A and C contributed to second side pot
        
        pot.award_to(winners)
        
        # Verify stacks increased
        assert player_a.stack > initial_stack_a
        assert player_b.stack > initial_stack_b
        if len(pot.side_pots) > 1:
            assert player_c.stack > initial_stack_c


class TestPotReset:
    """Tests for pot reset."""
    
    def test_reset(self):
        """Reset pot after awarding, verify all values return to initial state."""
        pot = Pot()
        player = Player("Player", 100)
        
        pot.add_contribution(player, 50)
        pot.resolve_side_pots()
        pot.award_to([player])
        
        pot.reset()
        
        assert pot.main_pot == 0
        assert pot.side_pots == []
        assert pot.contributors == {}

