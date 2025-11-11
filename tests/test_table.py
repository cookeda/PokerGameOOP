"""
Tests for Table class (initialization, player management, active players, reset).
"""
import pytest
from src.core.Table import Table
from src.core.Player import Player
from src.core.Pot import Pot


class TestTableInitialization:
    """Tests for table initialization."""
    
    def test_default_creation(self):
        """Create table with default 6 seats."""
        table = Table()
        assert len(table.seats) == 6
        assert table.small_blind == 1
        assert table.big_blind == 2
        assert table.dealer_button == 0
        assert table.community_cards == []
        assert isinstance(table.pot, Pot)
    
    def test_custom_seats(self):
        """Create table with custom number of seats."""
        table = Table(n_seats=9)
        assert len(table.seats) == 9
    
    def test_blinds(self):
        """Verify small_blind and big_blind set correctly."""
        table = Table(small_blind=5, big_blind=10)
        assert table.small_blind == 5
        assert table.big_blind == 10
    
    def test_initial_state(self):
        """Verify pot, dealer_button, community_cards initialized."""
        table = Table()
        assert isinstance(table.pot, Pot)
        assert table.dealer_button == 0
        assert table.community_cards == []
        assert table.dealer is None


class TestTablePlayerManagement:
    """Tests for player management."""
    
    @pytest.fixture
    def table(self):
        """Create a test table."""
        return Table(n_seats=6)
    
    @pytest.fixture
    def players(self):
        """Create test players."""
        return [
            Player("Player1", 100),
            Player("Player2", 100),
            Player("Player3", 100),
        ]
    
    def test_add_player(self, table, players):
        """Add player to table, verify assigned to seat."""
        player = players[0]
        seat_index = table.add_player(player)
        
        assert table.seats[seat_index].player == player
        assert player.seat_position == seat_index
    
    def test_add_player_specific_seat(self, table, players):
        """Add player to specific seat index."""
        player = players[0]
        seat_index = table.add_player(player, seat_index=3)
        
        assert seat_index == 3
        assert table.seats[3].player == player
        assert player.seat_position == 3
    
    def test_add_player_auto_seat(self, table, players):
        """Add player without specifying seat, verify assigned to first available."""
        player1 = players[0]
        player2 = players[1]
        
        seat1 = table.add_player(player1)
        seat2 = table.add_player(player2)
        
        assert seat1 == 0
        assert seat2 == 1
        assert table.seats[0].player == player1
        assert table.seats[1].player == player2
    
    def test_add_player_full_table(self, table):
        """Attempt to add player when table full, verify error."""
        # Fill all seats
        for i in range(6):
            player = Player(f"Player{i}", 100)
            table.add_player(player, seat_index=i)
        
        # Try to add one more
        extra_player = Player("Extra", 100)
        with pytest.raises(ValueError, match="No available seats"):
            table.add_player(extra_player)
    
    def test_add_player_occupied_seat(self, table, players):
        """Attempt to add player to occupied seat, verify error."""
        player1 = players[0]
        player2 = players[1]
        
        table.add_player(player1, seat_index=2)
        
        with pytest.raises(ValueError, match="already occupied"):
            table.add_player(player2, seat_index=2)
    
    def test_remove_player(self, table, players):
        """Remove player from table, verify seat cleared."""
        player = players[0]
        seat_index = table.add_player(player, seat_index=2)
        
        table.remove_player(player)
        
        assert table.seats[seat_index].player is None
        assert player.seat_position is None
    
    def test_remove_player_not_found(self, table):
        """Attempt to remove non-existent player, verify error."""
        player = Player("NotAtTable", 100)
        
        with pytest.raises(ValueError, match="not found"):
            table.remove_player(player)


class TestTableActivePlayerManagement:
    """Tests for active player management."""
    
    @pytest.fixture
    def table_with_players(self):
        """Create table with players."""
        table = Table(n_seats=6)
        players = [
            Player("Player1", 100),
            Player("Player2", 100),
            Player("Player3", 100),
        ]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        return table, players
    
    def test_get_active_players(self, table_with_players):
        """Get list of active players, verify only active players returned."""
        table, players = table_with_players
        
        active = table.get_active_players()
        assert len(active) == 3
        assert all(p in active for p in players)
        
        # Fold one player
        players[1].fold()
        active = table.get_active_players()
        assert len(active) == 2
        assert players[1] not in active
    
    def test_get_next_active_player(self, table_with_players):
        """Find next active player from current position."""
        table, players = table_with_players
        
        next_player, next_pos = table.get_next_active_player(0)
        assert next_player == players[1]
        assert next_pos == 1
    
    def test_get_next_active_player_wraps(self, table_with_players):
        """Verify wraps around table correctly."""
        table, players = table_with_players
        
        # Start from last player, should wrap to first
        next_player, next_pos = table.get_next_active_player(2)
        assert next_player == players[0]
        assert next_pos == 0
    
    def test_get_next_active_player_skips_folded(self, table_with_players):
        """Verify folded players are skipped."""
        table, players = table_with_players
        players[1].fold()
        
        next_player, next_pos = table.get_next_active_player(0)
        assert next_player == players[2]
        assert next_pos == 2
    
    def test_get_next_active_player_skips_all_in(self, table_with_players):
        """Verify all-in players are skipped."""
        table, players = table_with_players
        players[1].is_all_in = True
        
        next_player, next_pos = table.get_next_active_player(0)
        assert next_player == players[2]
        assert next_pos == 2
    
    def test_get_next_active_player_none(self):
        """No active players, verify returns None."""
        table = Table(n_seats=6)
        player = Player("Player", 100)
        table.add_player(player, seat_index=0)
        player.fold()
        
        next_player, next_pos = table.get_next_active_player(0)
        assert next_player is None
        assert next_pos is None


class TestTableReset:
    """Tests for table reset."""
    
    def test_reset_hand(self):
        """Reset table for new hand, verify community cards cleared, pot reset, players reset."""
        table = Table()
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        
        # Set up some state
        table.community_cards = [1, 2, 3]  # Mock cards
        table.pot.add_contribution(player1, 50)
        player1.current_bet = 50
        player1.has_folded = True
        player2.current_bet = 30
        
        table.reset_hand()
        
        assert table.community_cards == []
        assert table.pot.main_pot == 0
        assert table.pot.contributors == {}
        assert player1.current_bet == 0
        assert player1.has_folded is False
        assert player1.is_active is True
        assert player2.current_bet == 0

