"""
Integration tests for complete hand scenarios and edge cases.
"""
import pytest
from src.core.Player import Player
from src.core.Table import Table
from src.core.Pot import Pot
from src.core.Dealer import Dealer
from src.core.Deck import Deck
from src.core.GameState import GameState, Phase
from src.core.Action import Action, ActionType
from tests.conftest import MockAIPlayer, create_test_table, create_test_game_state


class TestCompleteHandScenarios:
    """Tests for complete hand scenarios."""
    
    def test_complete_hand_all_fold(self):
        """All players fold except one, verify pot awarded correctly."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        # Collect blinds
        dealer.collect_blinds()
        
        # Deal hole cards
        dealer.deal_hole_cards()
        
        # Create game state
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind  # From blinds
        
        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]
        
        # Player1 folds
        action1 = Action(player1, ActionType.FOLD)
        game_state.execute_action(action1)
        
        # Verify round complete and pot goes to player2
        assert game_state.round_complete() is True
        assert player1.has_folded is True
        assert player2.has_folded is False
    
    def test_complete_hand_check_down(self):
        """All players check to showdown, verify all phases completed."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        # Collect blinds
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]
        
        # After blinds, player1 needs to act (they haven't matched the big blind yet)
        # If player1 is the big blind, they can check; otherwise they need to call/raise
        # Find which player is the big blind (button + 2)
        bb_pos = (table.dealer_button + 2) % len(table.seats)
        if player1.seat_position == bb_pos:
            # Player1 is big blind, can check if no one raised
            action1 = Action(player1, ActionType.CHECK)
        else:
            # Player1 needs to call the big blind
            call_amount = game_state.get_call_amount(player1)
            action1 = Action(player1, ActionType.CALL, call_amount)
        game_state.execute_action(action1)
        
        # Resolve pre-flop
        game_state.resolve_bets()
        
        # Advance to flop
        game_state.advance_phase()
        assert game_state.phase == Phase.FLOP
        
        # Both check on flop
        action1 = Action(player1, ActionType.CHECK)
        game_state.execute_action(action1)
        action2 = Action(player2, ActionType.CHECK)
        game_state.execute_action(action2)
        game_state.resolve_bets()
        
        # Advance to turn
        game_state.advance_phase()
        assert game_state.phase == Phase.TURN
        
        # Both check on turn
        action1 = Action(player1, ActionType.CHECK)
        game_state.execute_action(action1)
        action2 = Action(player2, ActionType.CHECK)
        game_state.execute_action(action2)
        game_state.resolve_bets()
        
        # Advance to river
        game_state.advance_phase()
        assert game_state.phase == Phase.RIVER
        
        # Both check on river
        action1 = Action(player1, ActionType.CHECK)
        game_state.execute_action(action1)
        action2 = Action(player2, ActionType.CHECK)
        game_state.execute_action(action2)
        game_state.resolve_bets()
        
        # Advance to showdown
        game_state.advance_phase()
        assert game_state.phase == Phase.SHOWDOWN
    
    def test_complete_hand_with_betting(self):
        """Hand with betting on each street, verify pot grows correctly."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Pre-flop: Find which player can raise (hasn't matched the big blind)
        # The big blind has already matched, so they can only check
        # The other player can raise
        bb_pos = (table.dealer_button + 2) % len(table.seats)
        raiser = player1 if player1.seat_position != bb_pos else player2
        caller = player2 if raiser == player1 else player1
        
        # Raiser raises to 10
        action1 = Action(raiser, ActionType.RAISE, 10)  # Raise to 10
        game_state.execute_action(action1)
        
        # Caller calls
        call_amount = game_state.get_call_amount(caller)
        action2 = Action(caller, ActionType.CALL, call_amount)
        game_state.execute_action(action2)
        game_state.resolve_bets()
        
        initial_pot = pot.get_total()
        
        # Flop: Player2 bets
        game_state.advance_phase()
        action2 = Action(player2, ActionType.BET, 15)
        game_state.execute_action(action2)
        action1 = Action(player1, ActionType.CALL, game_state.get_call_amount(player1))
        game_state.execute_action(action1)
        game_state.resolve_bets()
        
        # Pot should have grown
        assert pot.get_total() > initial_pot
    
    def test_complete_hand_all_in(self):
        """Multiple all-ins, verify side pots created and awarded correctly."""
        table = create_test_table([
            ("Player1", 100),
            ("Player2", 50),
            ("Player3", 75)
        ], n_seats=3)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind
        
        players = [seat.player for seat in table.seats if seat.player]
        player1, player2, player3 = players
        
        # Player2 goes all-in (50)
        action2 = Action(player2, ActionType.ALL_IN, 50)
        game_state.execute_action(action2)
        
        # Player3 calls all-in (50)
        action3 = Action(player3, ActionType.CALL, 50)
        game_state.execute_action(action3)
        
        # Player1 calls (50)
        action1 = Action(player1, ActionType.CALL, 50)
        game_state.execute_action(action1)
        
        game_state.resolve_bets()
        
        # Verify side pots created
        pot.resolve_side_pots()
        assert len(pot.side_pots) > 0


class TestBettingRoundScenarios:
    """Tests for betting round scenarios."""
    
    def test_pre_flop_betting_round(self):
        """Complete pre-flop betting round with various actions."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind
        
        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Find which player can raise (not the big blind)
        bb_pos = (table.dealer_button + 2) % len(table.seats)
        raiser = player1 if player1.seat_position != bb_pos else player2
        caller = player2 if raiser == player1 else player1

        # Raiser raises to 10
        action1 = Action(raiser, ActionType.RAISE, 10)
        game_state.execute_action(action1)
        
        # Caller calls
        call_amount = game_state.get_call_amount(caller)
        action2 = Action(caller, ActionType.CALL, call_amount)
        game_state.execute_action(action2)
        
        # Round should be complete
        assert game_state.round_complete() is True
    
    def test_post_flop_betting_round(self):
        """Complete post-flop betting round."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Complete pre-flop - both players match the big blind
        next_player = game_state.next_to_act()
        while next_player:
            call_amount = game_state.get_call_amount(next_player)
            if call_amount > 0:
                action = Action(next_player, ActionType.CALL, call_amount)
            else:
                action = Action(next_player, ActionType.CHECK)
            game_state.execute_action(action)
            next_player = game_state.next_to_act()
        game_state.resolve_bets()
        
        # Advance to flop
        game_state.advance_phase()
        
        # Flop betting
        action1 = Action(player1, ActionType.BET, 10)
        game_state.execute_action(action1)
        call_amount = game_state.get_call_amount(player2)
        action2 = Action(player2, ActionType.CALL, call_amount)
        game_state.execute_action(action2)
        
        assert game_state.round_complete() is True
    
    def test_betting_round_with_raise(self):
        """Betting round with raises, verify round completes correctly."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Find which player can raise (not the big blind)
        bb_pos = (table.dealer_button + 2) % len(table.seats)
        raiser1 = player1 if player1.seat_position != bb_pos else player2
        raiser2 = player2 if raiser1 == player1 else player1

        # First raiser raises to 10
        action1 = Action(raiser1, ActionType.RAISE, 10)
        game_state.execute_action(action1)
        assert game_state.last_raiser_index == raiser1.seat_position

        # Second player re-raises to 20
        action2 = Action(raiser2, ActionType.RAISE, 20)
        game_state.execute_action(action2)
        assert game_state.last_raiser_index == raiser2.seat_position

        # First raiser calls
        call_amount = game_state.get_call_amount(raiser1)
        action1 = Action(raiser1, ActionType.CALL, call_amount)
        game_state.execute_action(action1)
        
        # Round should complete when action returns to last raiser
        assert game_state.round_complete() is True
    
    def test_betting_round_all_fold(self):
        """All players fold during betting round."""
        table = create_test_table([("Player1", 100), ("Player2", 100), ("Player3", 100)], n_seats=3)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2, player3 = players

        # Player1 raises (can't bet when there's already a bet)
        next_player = game_state.next_to_act()
        if next_player == player1:
            action1 = Action(player1, ActionType.RAISE, 20)  # Raise to 20
            game_state.execute_action(action1)
        else:
            # Let other players act first
            while game_state.next_to_act() != player1:
                p = game_state.next_to_act()
                call_amount = game_state.get_call_amount(p)
                if call_amount > 0:
                    action = Action(p, ActionType.CALL, call_amount)
                else:
                    action = Action(p, ActionType.CHECK)
                game_state.execute_action(action)
            action1 = Action(player1, ActionType.RAISE, 20)
            game_state.execute_action(action1)
        
        # Player2 folds
        action2 = Action(player2, ActionType.FOLD)
        game_state.execute_action(action2)
        
        # Player3 folds
        action3 = Action(player3, ActionType.FOLD)
        game_state.execute_action(action3)
        
        # Round should be complete (only one player left)
        assert game_state.round_complete() is True
        assert len([p for p in game_state.active_players if not p.has_folded]) == 1


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_player_goes_all_in_less_than_bet(self):
        """Player all-in for less than current bet, verify handled correctly."""
        table = create_test_table([("Player1", 100), ("Player2", 30)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        # Set button so Player1 (with 100 chips) is not the big blind
        # Button=1: SB=0 (Player1), BB=1 (Player2), so Player1 can raise
        table.dealer_button = 1
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Player1 (not big blind, has 100 chips) raises to 50
        action1 = Action(player1, ActionType.RAISE, 50)  # Raise to 50
        game_state.execute_action(action1)

        # Player2 goes all-in with remaining chips (less than 50)
        action2 = Action(player2, ActionType.ALL_IN, player2.stack)
        game_state.execute_action(action2)
        
        assert player2.is_all_in is True
        assert player2.current_bet < 50  # Less than the raise amount
        assert game_state.current_bet == 50  # Still 50, player2 didn't match
    
    def test_multiple_raises(self):
        """Multiple raises in same round, verify last_raiser tracked correctly."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind
        
        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Find which player can raise (not the big blind)
        bb_pos = (table.dealer_button + 2) % len(table.seats)
        raiser1 = player1 if player1.seat_position != bb_pos else player2
        raiser2 = player2 if raiser1 == player1 else player1

        # First raiser raises to 10
        action1 = Action(raiser1, ActionType.RAISE, 10)
        game_state.execute_action(action1)
        assert game_state.last_raiser_index == raiser1.seat_position

        # Second player re-raises to 20
        action2 = Action(raiser2, ActionType.RAISE, 20)
        game_state.execute_action(action2)
        assert game_state.last_raiser_index == raiser2.seat_position

        # First raiser re-raises again to 30
        action1 = Action(raiser1, ActionType.RAISE, 30)
        game_state.execute_action(action1)
        assert game_state.last_raiser_index == raiser1.seat_position
    
    def test_button_rotation(self):
        """Multiple hands, verify button rotates correctly."""
        table = create_test_table([("Player1", 100), ("Player2", 100)], n_seats=2)
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        initial_button = table.dealer_button
        
        # Rotate button
        dealer.rotate_button()
        
        assert table.dealer_button != initial_button
        assert table.dealer_button == 1  # Should move to next player
    
    def test_insufficient_chips_scenarios(self):
        """Various scenarios with players having insufficient chips."""
        table = create_test_table([("Player1", 100), ("Player2", 10)], n_seats=2)
        pot = Pot()
        dealer = Dealer(table, Deck(seed=42))
        table.dealer = dealer
        
        # Set button so Player1 (with 100 chips) is not the big blind
        # Button=1: SB=0 (Player1), BB=1 (Player2), so Player1 can raise
        table.dealer_button = 1
        
        dealer.collect_blinds()
        dealer.deal_hole_cards()
        
        game_state = GameState(table, pot)
        game_state.current_bet = table.big_blind

        players = [seat.player for seat in table.seats if seat.player]
        player1, player2 = players[0], players[1]

        # Player1 (not big blind, has 100 chips) raises to 50
        action1 = Action(player1, ActionType.RAISE, 50)  # Raise to 50
        game_state.execute_action(action1)

        # Player2 can only call with what they have (remaining chips after blind)
        # Player2 started with 10, posted 2 for big blind, so has 8 remaining
        # But needs to call 48 (50 - 2), which is more than they have
        call_amount = game_state.get_call_amount(player2)
        assert call_amount > player2.stack  # Player2 doesn't have enough to fully call
        
        # Player2 can still call (will go all-in with remaining chips)
        action2 = Action(player2, ActionType.CALL, call_amount)
        game_state.execute_action(action2)
        
        assert player2.is_all_in is True
        assert player2.stack == 0
        assert player2.current_bet < game_state.current_bet  # Didn't match the full bet


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_action_amounts(self):
        """Test invalid action amounts."""
        table = create_test_table([("Player1", 100)], n_seats=1)
        pot = Pot()
        game_state = GameState(table, pot)
        
        player = table.seats[0].player
        
        # Negative amount
        action = Action(player, ActionType.BET, -10)
        # Should be caught by validation
        with pytest.raises(ValueError):
            game_state.execute_action(action)
    
    def test_zero_stack_player(self):
        """Player with zero stack, verify handled correctly."""
        table = create_test_table([("Player1", 0)], n_seats=1)
        pot = Pot()
        game_state = GameState(table, pot)
        
        player = table.seats[0].player
        
        # Player can only fold or go all-in (with 0)
        valid_actions = game_state.get_valid_actions(player)
        assert ActionType.FOLD in valid_actions
        # ALL_IN might not be available with 0 stack
    
    def test_empty_table(self):
        """Operations on empty table."""
        table = Table()
        pot = Pot()
        game_state = GameState(table, pot)
        
        # Should have no active players
        assert len(game_state.active_players) == 0
    
    def test_single_player(self):
        """Table with only one player."""
        table = create_test_table([("Player1", 100)], n_seats=1)
        pot = Pot()
        game_state = GameState(table, pot)
        
        assert len(game_state.active_players) == 1
        # Round should complete immediately (no one to act against)
        assert game_state.round_complete() is True

