from enum import Enum
from src.core.Action import Action, ActionType
from src.core.Pot import Pot
from src.core.Table import Table

class Phase(Enum):
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class GameState:
    def __init__(self, table: Table, pot: Pot):
        self.table = table
        self.pot = pot
        self.phase = Phase.PRE_FLOP
        self.current_bet = 0  # Highest bet this round
        self.to_act_index = None  # Current player position
        self.last_raiser_index = None  # Last player to raise (for round completion)
        self.min_raise = table.big_blind  # Minimum raise amount
        self.action_history = []  # List of actions this round
        
        # Initialize active players
        self.active_players = table.get_active_players()
        
        # Set starting position (left of big blind for pre-flop)
        if self.phase == Phase.PRE_FLOP:
            # Start left of big blind (3 positions after button)
            n_seats = len(table.seats)
            self.to_act_index = (table.dealer_button + 3) % n_seats
        else:
            # Post-flop starts left of button
            self.to_act_index = (table.dealer_button + 1) % len(table.seats)
    
    def next_to_act(self):
        """Return the next player who needs to act."""
        if self.round_complete():
            return None
        
        n_seats = len(self.table.seats)
        start_index = self.to_act_index
        
        # Find next active player
        for i in range(n_seats):
            pos = (start_index + i) % n_seats
            seat = self.table.seats[pos]
            
            if seat.player and seat.player.is_active and not seat.player.has_folded and not seat.player.is_all_in:
                # Check if player needs to act (hasn't matched current bet)
                if seat.player.current_bet < self.current_bet:
                    self.to_act_index = pos
                    return seat.player
        
        # No one needs to act
        return None
    
    def get_call_amount(self, player):
        """Calculate the amount a player needs to call."""
        return max(0, self.current_bet - player.current_bet)
    
    def get_valid_actions(self, player):
        """Return list of valid actions for a player."""
        valid_actions = []
        call_amount = self.get_call_amount(player)
        
        # Always can fold
        valid_actions.append(ActionType.FOLD)
        
        if call_amount == 0:
            # Can check
            valid_actions.append(ActionType.CHECK)
            # Can bet (if no one has bet yet)
            if self.current_bet == 0:
                if player.stack > 0:
                    valid_actions.append(ActionType.BET)
        else:
            # Must call or raise
            if call_amount <= player.stack:
                valid_actions.append(ActionType.CALL)
            else:
                # Can only call all-in
                valid_actions.append(ActionType.CALL)
            
            # Can raise if has enough chips
            min_raise_amount = self.current_bet + self.min_raise
            total_needed = min_raise_amount - player.current_bet
            if total_needed <= player.stack:
                valid_actions.append(ActionType.RAISE)
        
        # Can always go all-in if has chips
        if player.stack > 0:
            valid_actions.append(ActionType.ALL_IN)
        
        return valid_actions
    
    def execute_action(self, action: Action):
        """
        Execute a player action with validation.
        Updates player state, game state, and pot.
        """
        player = action.player
        
        # Validate player is active
        if not player.is_active or player.has_folded or player.is_all_in:
            raise ValueError(f"Player {player.name} cannot act")
        
        # Validate action is legal
        valid_actions = self.get_valid_actions(player)
        if action.type not in valid_actions:
            raise ValueError(f"Invalid action {action.type.value} for player {player.name}")
        
        # Execute the action
        amount_contributed = 0
        
        if action.type == ActionType.FOLD:
            player.fold()
            self.active_players = [p for p in self.active_players if p != player]
        
        elif action.type == ActionType.CHECK:
            if self.get_call_amount(player) > 0:
                raise ValueError("Cannot check when there is a bet to call")
            player.check()
        
        elif action.type == ActionType.CALL:
            call_amount = self.get_call_amount(player)
            if call_amount > 0:
                amount_contributed = player.call(call_amount)
                self.pot.add_contribution(player, amount_contributed)
        
        elif action.type == ActionType.BET:
            if self.current_bet > 0:
                raise ValueError("Cannot bet when there is already a bet (use raise instead)")
            if action.amount < self.min_raise:
                raise ValueError(f"Bet must be at least {self.min_raise}")
            if action.amount > player.stack:
                raise ValueError("Cannot bet more than stack")
            amount_contributed = player.bet(action.amount)
            self.pot.add_contribution(player, amount_contributed)
            self.current_bet = player.current_bet
            self.last_raiser_index = player.seat_position
        
        elif action.type == ActionType.RAISE:
            # action.amount is the total bet amount (not just the raise increment)
            min_total_bet = self.current_bet + self.min_raise
            if action.amount < min_total_bet:
                raise ValueError(f"Raise must be at least {min_total_bet} (current bet {self.current_bet} + min raise {self.min_raise})")
            if action.amount > player.stack + player.current_bet:
                raise ValueError("Cannot raise more than available chips")
            
            # Calculate actual raise amount (additional chips needed)
            raise_amount = action.amount - player.current_bet
            if raise_amount > player.stack:
                raise ValueError("Cannot raise more than available chips")
            
            amount_contributed = player.bet(raise_amount)
            self.pot.add_contribution(player, amount_contributed)
            self.current_bet = player.current_bet
            self.last_raiser_index = player.seat_position
        
        elif action.type == ActionType.ALL_IN:
            amount_contributed = player.all_in()
            self.pot.add_contribution(player, amount_contributed)
            if player.current_bet > self.current_bet:
                self.current_bet = player.current_bet
                self.last_raiser_index = player.seat_position
        
        # Update action history
        self.action_history.append(action)
        
        # Move to next player
        if action.type != ActionType.FOLD:
            n_seats = len(self.table.seats)
            self.to_act_index = (player.seat_position + 1) % n_seats
    
    def round_complete(self):
        """
        Check if the betting round is complete.
        Round is complete when all active players have matched the current bet
        and action has returned to the last raiser (or no one has raised).
        """
        # Check if only one player remains
        active_count = sum(1 for p in self.active_players if not p.has_folded)
        if active_count <= 1:
            return True
        
        # Check if all active players have matched the bet
        for player in self.active_players:
            if not player.has_folded and not player.is_all_in:
                if player.current_bet < self.current_bet:
                    return False
        
        # If no one raised, round is complete when all have acted
        if self.last_raiser_index is None:
            return True
        
        # Round is complete when action returns to last raiser
        # (all players after the raiser have matched the bet)
        n_seats = len(self.table.seats)
        raiser_pos = self.last_raiser_index
        
        # Check all players after the raiser have matched
        for i in range(1, n_seats):
            pos = (raiser_pos + i) % n_seats
            seat = self.table.seats[pos]
            
            if seat.player and seat.player.is_active and not seat.player.has_folded:
                if not seat.player.is_all_in and seat.player.current_bet < self.current_bet:
                    return False
                
                # If we've cycled back to raiser, round is complete
                if pos == raiser_pos:
                    return True
        
        return True
    
    def resolve_bets(self):
        """Finalize bets at the end of a betting round."""
        # Reset current bet for next round
        self.current_bet = 0
        self.last_raiser_index = None
        self.action_history = []
        
        # Reset player current_bet (but keep contributions in pot)
        for player in self.active_players:
            player.current_bet = 0
    
    def advance_phase(self):
        """Advance to the next phase of the hand."""
        if self.phase == Phase.PRE_FLOP:
            self.phase = Phase.FLOP
            self.table.dealer.deal_community("FLOP")
            self.resolve_bets()
            # Reset to act to left of button
            self.to_act_index = (self.table.dealer_button + 1) % len(self.table.seats)
        
        elif self.phase == Phase.FLOP:
            self.phase = Phase.TURN
            self.table.dealer.deal_community("TURN")
            self.resolve_bets()
            self.to_act_index = (self.table.dealer_button + 1) % len(self.table.seats)
        
        elif self.phase == Phase.TURN:
            self.phase = Phase.RIVER
            self.table.dealer.deal_community("RIVER")
            self.resolve_bets()
            self.to_act_index = (self.table.dealer_button + 1) % len(self.table.seats)
        
        elif self.phase == Phase.RIVER:
            self.phase = Phase.SHOWDOWN
            self.resolve_bets()
        
        else:
            raise ValueError(f"Cannot advance from phase {self.phase}")
    
    def showdown(self):
        """Handle the showdown phase."""
        self.phase = Phase.SHOWDOWN
        # Hand evaluation and pot distribution would happen here
        # This is a placeholder - actual hand evaluation would be implemented separately
        pass

