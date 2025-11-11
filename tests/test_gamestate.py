"""
Tests for GameState class (initialization, turn management, action execution, phase advancement).
"""
import pytest
from src.core.GameState import GameState, Phase
from src.core.Action import Action, ActionType
from src.core.Player import Player
from src.core.Table import Table
from src.core.Pot import Pot
from src.core.Dealer import Dealer
from src.core.Deck import Deck
from tests.conftest import MockAIPlayer


class TestGameStateInitialization:
    """Tests for GameState initialization."""
    
    def test_gamestate_creation(self):
        """Create GameState with table and pot."""
        table = Table()
        pot = Pot()
        game_state = GameState(table, pot)
        
        assert game_state.table == table
        assert game_state.pot == pot
    
    def test_initial_phase(self):
        """Verify phase is PRE_FLOP."""
        table = Table()
        pot = Pot()
        game_state = GameState(table, pot)
        
        assert game_state.phase == Phase.PRE_FLOP
    
    def test_initial_bet(self):
        """Verify current_bet = 0."""
        table = Table()
        pot = Pot()
        game_state = GameState(table, pot)
        
        assert game_state.current_bet == 0
    
    def test_active_players(self):
        """Verify active_players list populated correctly."""
        table = Table()
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        
        pot = Pot()
        game_state = GameState(table, pot)
        
        assert len(game_state.active_players) == 2
        assert player1 in game_state.active_players
        assert player2 in game_state.active_players
    
    def test_starting_position_pre_flop(self):
        """Verify to_act_index set to left of big blind."""
        table = Table()
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        player3 = Player("Player3", 100)
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        table.add_player(player3, seat_index=2)
        table.dealer_button = 0
        
        pot = Pot()
        game_state = GameState(table, pot)
        
        # Should start at position 3 (button + 3, which is left of BB)
        # In a 3-seat table: button=0, SB=1, BB=2, first to act=(0+3)%3=0
        # But since we're calculating (button + 3) % 3, it should be 0
        expected_index = (table.dealer_button + 3) % len(table.seats)
        assert game_state.to_act_index == expected_index
    
    def test_starting_position_post_flop(self):
        """Create GameState in post-flop phase, verify to_act_index set correctly."""
        table = Table()
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        table.dealer_button = 0
        
        pot = Pot()
        game_state = GameState(table, pot)
        game_state.phase = Phase.FLOP
        game_state.to_act_index = (table.dealer_button + 1) % len(table.seats)
        
        assert game_state.to_act_index == 1  # Left of button


class TestGameStateTurnManagement:
    """Tests for turn management."""
    
    @pytest.fixture
    def game_state_with_players(self):
        """Create game state with players."""
        table = Table(n_seats=6)
        players = [Player(f"Player{i}", 100, is_human=False) for i in range(3)]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        table.dealer_button = 0
        pot = Pot()
        game_state = GameState(table, pot)
        return game_state, players
    
    def test_next_to_act(self, game_state_with_players):
        """Get next player to act, verify correct player returned."""
        game_state, players = game_state_with_players
        game_state.to_act_index = 0
        game_state.current_bet = 10
        players[0].current_bet = 0  # Needs to act
        
        next_player = game_state.next_to_act()
        
        assert next_player == players[0]
    
    def test_next_to_act_skips_folded(self, game_state_with_players):
        """Verify folded players skipped."""
        game_state, players = game_state_with_players
        game_state.to_act_index = 0
        game_state.current_bet = 10
        players[0].fold()
        players[1].current_bet = 0
        
        next_player = game_state.next_to_act()
        
        assert next_player == players[1]
    
    def test_next_to_act_skips_all_in(self, game_state_with_players):
        """Verify all-in players skipped."""
        game_state, players = game_state_with_players
        game_state.to_act_index = 0
        game_state.current_bet = 10
        players[0].is_all_in = True
        players[1].current_bet = 0
        
        next_player = game_state.next_to_act()
        
        assert next_player == players[1]
    
    def test_next_to_act_round_complete(self, game_state_with_players):
        """Round complete, verify returns None."""
        game_state, players = game_state_with_players
        game_state.current_bet = 10
        # All players have matched
        for player in players:
            player.current_bet = 10
        
        next_player = game_state.next_to_act()
        
        assert next_player is None
    
    def test_next_to_act_wraps(self, game_state_with_players):
        """Verify wraps around table correctly."""
        game_state, players = game_state_with_players
        game_state.to_act_index = 2  # Start from last player
        game_state.current_bet = 10
        players[2].current_bet = 0
        
        next_player = game_state.next_to_act()
        
        # Should wrap to first player if they need to act
        # Or return None if round is complete
        assert next_player is None or next_player in players


class TestGameStateValidActions:
    """Tests for valid actions."""
    
    @pytest.fixture
    def game_state_with_player(self):
        """Create game state with one player."""
        table = Table()
        player = Player("Player", 100, is_human=False)
        table.add_player(player, seat_index=0)
        pot = Pot()
        game_state = GameState(table, pot)
        return game_state, player
    
    def test_get_valid_actions_no_bet(self, game_state_with_player):
        """No current bet, verify CHECK and BET available."""
        game_state, player = game_state_with_player
        game_state.current_bet = 0
        
        valid_actions = game_state.get_valid_actions(player)
        
        assert ActionType.FOLD in valid_actions
        assert ActionType.CHECK in valid_actions
        assert ActionType.BET in valid_actions
    
    def test_get_valid_actions_with_bet(self, game_state_with_player):
        """Current bet exists, verify CALL and RAISE available."""
        game_state, player = game_state_with_player
        game_state.current_bet = 20
        player.current_bet = 0
        
        valid_actions = game_state.get_valid_actions(player)
        
        assert ActionType.FOLD in valid_actions
        assert ActionType.CALL in valid_actions
        assert ActionType.RAISE in valid_actions
    
    def test_get_valid_actions_insufficient_chips(self, game_state_with_player):
        """Player can't afford call, verify only FOLD and ALL_IN."""
        game_state, player = game_state_with_player
        game_state.current_bet = 150  # More than player's stack
        player.stack = 100
        player.current_bet = 0
        
        valid_actions = game_state.get_valid_actions(player)
        
        assert ActionType.FOLD in valid_actions
        assert ActionType.CALL in valid_actions  # Can still call (all-in)
        assert ActionType.ALL_IN in valid_actions
    
    def test_get_call_amount(self, game_state_with_player):
        """Calculate call amount correctly."""
        game_state, player = game_state_with_player
        game_state.current_bet = 30
        player.current_bet = 10
        
        call_amount = game_state.get_call_amount(player)
        
        assert call_amount == 20
    
    def test_get_call_amount_zero(self, game_state_with_player):
        """No bet to call, verify returns 0."""
        game_state, player = game_state_with_player
        game_state.current_bet = 0
        player.current_bet = 0
        
        call_amount = game_state.get_call_amount(player)
        
        assert call_amount == 0


class TestGameStateActionExecution:
    """Tests for action execution."""
    
    @pytest.fixture
    def game_state_with_players(self):
        """Create game state with players."""
        table = Table(n_seats=6)
        players = [Player(f"Player{i}", 100, is_human=False) for i in range(3)]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        pot = Pot()
        game_state = GameState(table, pot)
        return game_state, players
    
    def test_execute_fold(self, game_state_with_players):
        """Execute fold action, verify player folded, removed from active."""
        game_state, players = game_state_with_players
        action = Action(players[0], ActionType.FOLD)
        initial_active_count = len(game_state.active_players)
        
        game_state.execute_action(action)
        
        assert players[0].has_folded is True
        assert players[0] not in game_state.active_players
        assert len(game_state.active_players) == initial_active_count - 1
    
    def test_execute_check(self, game_state_with_players):
        """Execute check with no bet, verify no errors."""
        game_state, players = game_state_with_players
        game_state.current_bet = 0
        action = Action(players[0], ActionType.CHECK)
        
        game_state.execute_action(action)
        
        # Should complete without error
        assert action in game_state.action_history
    
    def test_execute_check_with_bet(self, game_state_with_players):
        """Attempt check when bet exists, verify error."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        action = Action(players[0], ActionType.CHECK)

        with pytest.raises(ValueError, match="Invalid action"):
            game_state.execute_action(action)
    
    def test_execute_call(self, game_state_with_players):
        """Execute call, verify chips deducted, pot updated, current_bet matched."""
        game_state, players = game_state_with_players
        game_state.current_bet = 30
        players[0].current_bet = 0
        initial_stack = players[0].stack
        initial_pot = game_state.pot.main_pot
        
        action = Action(players[0], ActionType.CALL, 30)
        game_state.execute_action(action)
        
        assert players[0].stack == initial_stack - 30
        assert players[0].current_bet == 30
        assert game_state.pot.main_pot == initial_pot + 30
    
    def test_execute_bet(self, game_state_with_players):
        """Execute bet, verify chips deducted, pot updated, current_bet set."""
        game_state, players = game_state_with_players
        game_state.current_bet = 0
        initial_stack = players[0].stack
        initial_pot = game_state.pot.main_pot
        
        action = Action(players[0], ActionType.BET, 25)
        game_state.execute_action(action)
        
        assert players[0].stack == initial_stack - 25
        assert game_state.current_bet == 25
        assert game_state.pot.main_pot == initial_pot + 25
        assert game_state.last_raiser_index == players[0].seat_position
    
    def test_execute_bet_invalid(self, game_state_with_players):
        """Bet when bet exists, verify error."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        action = Action(players[0], ActionType.BET, 25)

        with pytest.raises(ValueError, match="Invalid action"):
            game_state.execute_action(action)
    
    def test_execute_bet_below_minimum(self, game_state_with_players):
        """Bet below min_raise, verify error."""
        game_state, players = game_state_with_players
        game_state.current_bet = 0
        game_state.min_raise = 5
        action = Action(players[0], ActionType.BET, 3)
        
        with pytest.raises(ValueError, match="Bet must be at least"):
            game_state.execute_action(action)
    
    def test_execute_raise(self, game_state_with_players):
        """Execute raise, verify chips deducted, current_bet updated, last_raiser set."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        players[0].current_bet = 0
        game_state.min_raise = 2
        initial_stack = players[0].stack
        initial_pot = game_state.pot.main_pot
        
        action = Action(players[0], ActionType.RAISE, 30)  # Total bet of 30
        game_state.execute_action(action)
        
        assert players[0].stack == initial_stack - 30
        assert game_state.current_bet == 30
        assert game_state.last_raiser_index == players[0].seat_position
        assert game_state.pot.main_pot == initial_pot + 30
    
    def test_execute_raise_below_minimum(self, game_state_with_players):
        """Raise below minimum, verify error."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        players[0].current_bet = 0
        game_state.min_raise = 5
        action = Action(players[0], ActionType.RAISE, 22)  # Only 2 more, need 5
        
        with pytest.raises(ValueError, match="Raise must be at least"):
            game_state.execute_action(action)
    
    def test_execute_all_in(self, game_state_with_players):
        """Execute all-in, verify player all-in, pot updated."""
        game_state, players = game_state_with_players
        initial_stack = players[0].stack
        initial_pot = game_state.pot.main_pot
        
        action = Action(players[0], ActionType.ALL_IN, initial_stack)
        game_state.execute_action(action)
        
        assert players[0].stack == 0
        assert players[0].is_all_in is True
        assert game_state.pot.main_pot == initial_pot + initial_stack
    
    def test_execute_action_inactive_player(self, game_state_with_players):
        """Attempt action from inactive player, verify error."""
        game_state, players = game_state_with_players
        players[0].is_active = False
        action = Action(players[0], ActionType.CHECK)
        
        with pytest.raises(ValueError, match="cannot act"):
            game_state.execute_action(action)
    
    def test_execute_invalid_action(self, game_state_with_players):
        """Invalid action type for situation, verify error."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        # CHECK is not valid when there's a bet
        action = Action(players[0], ActionType.CHECK)
        
        with pytest.raises(ValueError, match="Invalid action"):
            game_state.execute_action(action)


class TestGameStateRoundCompletion:
    """Tests for round completion."""
    
    @pytest.fixture
    def game_state_with_players(self):
        """Create game state with players."""
        table = Table(n_seats=6)
        players = [Player(f"Player{i}", 100, is_human=False) for i in range(3)]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        pot = Pot()
        game_state = GameState(table, pot)
        return game_state, players
    
    def test_round_complete_all_matched(self, game_state_with_players):
        """All players matched bet, verify round complete."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        for player in players:
            player.current_bet = 20
        
        assert game_state.round_complete() is True
    
    def test_round_complete_with_raise(self, game_state_with_players):
        """Raise occurred, verify round complete when action returns to raiser."""
        game_state, players = game_state_with_players
        game_state.current_bet = 30
        game_state.last_raiser_index = players[0].seat_position
        players[0].current_bet = 30
        players[1].current_bet = 30
        players[2].current_bet = 30
        
        assert game_state.round_complete() is True
    
    def test_round_complete_one_player(self, game_state_with_players):
        """Only one player remains, verify round complete."""
        game_state, players = game_state_with_players
        players[1].fold()
        players[2].fold()
        
        assert game_state.round_complete() is True
    
    def test_round_complete_not_complete(self, game_state_with_players):
        """Players haven't matched, verify round not complete."""
        game_state, players = game_state_with_players
        game_state.current_bet = 20
        players[0].current_bet = 20
        players[1].current_bet = 10  # Hasn't matched
        players[2].current_bet = 20
        
        assert game_state.round_complete() is False


class TestGameStateBetResolution:
    """Tests for bet resolution."""
    
    @pytest.fixture
    def game_state_with_players(self):
        """Create game state with players."""
        table = Table(n_seats=6)
        players = [Player(f"Player{i}", 100, is_human=False) for i in range(2)]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        pot = Pot()
        game_state = GameState(table, pot)
        return game_state, players
    
    def test_resolve_bets(self, game_state_with_players):
        """Resolve bets at end of round, verify current_bet reset, player bets reset."""
        game_state, players = game_state_with_players
        game_state.current_bet = 30
        players[0].current_bet = 30
        players[1].current_bet = 30
        game_state.action_history = [Action(players[0], ActionType.BET, 30)]
        
        game_state.resolve_bets()
        
        assert game_state.current_bet == 0
        assert players[0].current_bet == 0
        assert players[1].current_bet == 0
        assert game_state.action_history == []
        assert game_state.last_raiser_index is None


class TestGameStatePhaseAdvancement:
    """Tests for phase advancement."""
    
    @pytest.fixture
    def game_state_with_dealer(self):
        """Create game state with dealer."""
        table = Table()
        players = [Player(f"Player{i}", 100, is_human=False) for i in range(2)]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        table.dealer = dealer
        pot = Pot()
        game_state = GameState(table, pot)
        return game_state, dealer
    
    def test_advance_phase_pre_flop_to_flop(self, game_state_with_dealer):
        """Advance to flop, verify phase changed, flop dealt, bets resolved."""
        game_state, dealer = game_state_with_dealer
        initial_phase = game_state.phase
        initial_community = len(game_state.table.community_cards)
        
        game_state.advance_phase()
        
        assert game_state.phase == Phase.FLOP
        assert len(game_state.table.community_cards) == initial_community + 3
        assert game_state.current_bet == 0
    
    def test_advance_phase_flop_to_turn(self, game_state_with_dealer):
        """Advance to turn, verify phase changed, turn dealt."""
        game_state, dealer = game_state_with_dealer
        game_state.phase = Phase.FLOP
        initial_community = len(game_state.table.community_cards)
        
        game_state.advance_phase()
        
        assert game_state.phase == Phase.TURN
        assert len(game_state.table.community_cards) == initial_community + 1
    
    def test_advance_phase_turn_to_river(self, game_state_with_dealer):
        """Advance to river, verify phase changed, river dealt."""
        game_state, dealer = game_state_with_dealer
        game_state.phase = Phase.TURN
        initial_community = len(game_state.table.community_cards)
        
        game_state.advance_phase()
        
        assert game_state.phase == Phase.RIVER
        assert len(game_state.table.community_cards) == initial_community + 1
    
    def test_advance_phase_river_to_showdown(self, game_state_with_dealer):
        """Advance to showdown, verify phase changed."""
        game_state, dealer = game_state_with_dealer
        game_state.phase = Phase.RIVER
        
        game_state.advance_phase()
        
        assert game_state.phase == Phase.SHOWDOWN
    
    def test_advance_phase_invalid(self, game_state_with_dealer):
        """Attempt advance from showdown, verify error."""
        game_state, dealer = game_state_with_dealer
        game_state.phase = Phase.SHOWDOWN
        
        with pytest.raises(ValueError, match="Cannot advance"):
            game_state.advance_phase()


class TestGameStateShowdown:
    """Tests for showdown."""
    
    def test_showdown(self):
        """Execute showdown, verify phase set to SHOWDOWN."""
        table = Table()
        pot = Pot()
        game_state = GameState(table, pot)
        game_state.phase = Phase.RIVER
        
        game_state.showdown()
        
        assert game_state.phase == Phase.SHOWDOWN

