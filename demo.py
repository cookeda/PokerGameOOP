"""
Simple demo script showing the poker game in action with random actions.
"""
import random
from src.core.Deck import Deck
from src.core.Table import Table
from src.core.Dealer import Dealer
from src.core.Player import Player
from src.core.Pot import Pot
from src.core.GameState import GameState, Phase
from src.core.Action import Action, ActionType

def print_separator():
    print("\n" + "="*60 + "\n")

class RandomAIPlayer(Player):
    """AI player that makes random valid actions."""
    
    def get_action(self, game_state):
        """Return a random valid action."""
        valid_actions = game_state.get_valid_actions(self)
        
        # Remove ALL_IN from random choices (too aggressive for demo)
        if ActionType.ALL_IN in valid_actions and len(valid_actions) > 1:
            valid_actions = [a for a in valid_actions if a != ActionType.ALL_IN]
        
        action_type = random.choice(valid_actions)
        
        if action_type == ActionType.FOLD:
            return Action(self, ActionType.FOLD)
        elif action_type == ActionType.CHECK:
            return Action(self, ActionType.CHECK)
        elif action_type == ActionType.CALL:
            call_amount = game_state.get_call_amount(self)
            return Action(self, ActionType.CALL, call_amount)
        elif action_type == ActionType.BET:
            # Random bet between min_raise and half of stack
            min_bet = game_state.min_raise
            max_bet = min(self.stack // 2, self.stack)
            bet_amount = random.randint(min_bet, max_bet) if max_bet >= min_bet else min_bet
            return Action(self, ActionType.BET, bet_amount)
        elif action_type == ActionType.RAISE:
            # Random raise between min_raise and half of stack
            call_amount = game_state.get_call_amount(self)
            min_raise_total = game_state.current_bet + game_state.min_raise
            max_raise_total = min(self.stack + self.current_bet, game_state.current_bet + self.stack // 2)
            raise_amount = random.randint(min_raise_total, max_raise_total) if max_raise_total >= min_raise_total else min_raise_total
            return Action(self, ActionType.RAISE, raise_amount)
        else:
            # Fallback to fold
            return Action(self, ActionType.FOLD)

def main():
    print("="*60)
    print("POKER GAME DEMO - RANDOM ACTIONS")
    print("="*60)
    
    # Create table with 2 players
    table = Table(n_seats=6, small_blind=1, big_blind=2)
    deck = Deck()  # Random seed for random cards
    dealer = Dealer(table, deck)
    table.dealer = dealer
    pot = Pot()
    
    # Add players with random AI
    player1 = RandomAIPlayer("Alice", 100, is_human=False)
    player2 = RandomAIPlayer("Bob", 100, is_human=False)
    table.add_player(player1, seat_index=0)
    table.add_player(player2, seat_index=1)
    
    print(f"\nPlayers at table:")
    print(f"  {player1.name}: {player1.stack} chips")
    print(f"  {player2.name}: {player2.stack} chips")
    
    print_separator()
    print("STEP 1: Collecting Blinds")
    print_separator()
    
    dealer.collect_blinds()
    print(f"Small Blind ({table.small_blind}): Posted by player at seat {(table.dealer_button + 1) % len(table.seats)}")
    print(f"Big Blind ({table.big_blind}): Posted by player at seat {(table.dealer_button + 2) % len(table.seats)}")
    print(f"Pot: {pot.get_total()} chips")
    print(f"  {player1.name}: {player1.stack} chips, current bet: {player1.current_bet}")
    print(f"  {player2.name}: {player2.stack} chips, current bet: {player2.current_bet}")
    
    print_separator()
    print("STEP 2: Dealing Hole Cards")
    print_separator()
    
    dealer.deal_hole_cards()
    print(f"{player1.name}'s hand: {[str(card) for card in player1.hand]}")
    print(f"{player2.name}'s hand: {[str(card) for card in player2.hand]}")
    
    print_separator()
    print("STEP 3: Pre-Flop Betting Round")
    print_separator()
    
    game_state = GameState(table, pot)
    game_state.current_bet = table.big_blind
    
    print(f"Current bet to match: {game_state.current_bet}")
    print(f"Pot: {pot.get_total()} chips")
    
    # Play betting round with random actions
    round_num = 1
    while not game_state.round_complete():
        player = game_state.next_to_act()
        if player is None:
            break
        
        action = player.decide_action(game_state)
        print(f"\n{player.name} {action.type.value.upper()}", end="")
        if action.amount > 0:
            print(f" {action.amount}", end="")
        print()
        
        game_state.execute_action(action)
        print(f"  {player.name}: {player.stack} chips, current bet: {player.current_bet}")
        print(f"  Pot: {pot.get_total()} chips")
        round_num += 1
    
    print(f"\nBetting round complete!")
    game_state.resolve_bets()
    
    print_separator()
    print("STEP 4: Dealing the Flop")
    print_separator()
    
    game_state.advance_phase()
    print(f"Community cards: {[str(card) for card in table.community_cards]}")
    print(f"Phase: {game_state.phase.value.upper()}")
    
    print_separator()
    print("STEP 5: Flop Betting Round")
    print_separator()
    
    # Play betting round with random actions
    round_num = 1
    while not game_state.round_complete():
        player = game_state.next_to_act()
        if player is None:
            break
        
        action = player.decide_action(game_state)
        print(f"\n{player.name} {action.type.value.upper()}", end="")
        if action.amount > 0:
            print(f" {action.amount}", end="")
        print()
        
        game_state.execute_action(action)
        print(f"  {player.name}: {player.stack} chips, current bet: {player.current_bet}")
        print(f"  Pot: {pot.get_total()} chips")
        round_num += 1
    
    print(f"\nBetting round complete!")
    game_state.resolve_bets()
    
    # Check if hand ended (only one player left)
    active_players = [p for p in game_state.active_players if not p.has_folded]
    if len(active_players) == 1:
        print_separator()
        print("HAND COMPLETE - PLAYER FOLDED!")
        print_separator()
        winner = active_players[0]
        print(f"Winner: {winner.name}")
        print(f"Final pot: {pot.get_total()} chips")
        pot.award_to([winner])
        print(f"\nFinal stacks:")
        print(f"  {player1.name}: {player1.stack} chips")
        print(f"  {player2.name}: {player2.stack} chips")
        print("\n" + "="*60)
        print("Demo complete!")
        print("="*60)
        return
    
    print_separator()
    print("STEP 6: Dealing the Turn")
    print_separator()
    
    game_state.advance_phase()
    print(f"Community cards: {[str(card) for card in table.community_cards]}")
    print(f"Phase: {game_state.phase.value.upper()}")
    
    print_separator()
    print("STEP 7: Turn Betting Round")
    print_separator()
    
    # Play betting round with random actions
    round_num = 1
    while not game_state.round_complete():
        player = game_state.next_to_act()
        if player is None:
            break
        
        action = player.decide_action(game_state)
        print(f"\n{player.name} {action.type.value.upper()}", end="")
        if action.amount > 0:
            print(f" {action.amount}", end="")
        print()
        
        game_state.execute_action(action)
        print(f"  {player.name}: {player.stack} chips, current bet: {player.current_bet}")
        print(f"  Pot: {pot.get_total()} chips")
        round_num += 1
        
        # Check if hand ended (only one player left)
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            print(f"\n{active_players[0].name} wins by default (opponent folded)!")
            break
    
    print(f"\nBetting round complete!")
    game_state.resolve_bets()
    
    # Check if hand ended
    active_players = [p for p in game_state.active_players if not p.has_folded]
    if len(active_players) == 1:
        print_separator()
        print("HAND COMPLETE - PLAYER FOLDED!")
        print_separator()
        winner = active_players[0]
        print(f"Winner: {winner.name}")
        print(f"Final pot: {pot.get_total()} chips")
        pot.award_to([winner])
        print(f"\nFinal stacks:")
        print(f"  {player1.name}: {player1.stack} chips")
        print(f"  {player2.name}: {player2.stack} chips")
        print("\n" + "="*60)
        print("Demo complete!")
        print("="*60)
        return
    
    print_separator()
    print("STEP 8: Dealing the River")
    print_separator()
    
    game_state.advance_phase()
    print(f"Community cards: {[str(card) for card in table.community_cards]}")
    print(f"Phase: {game_state.phase.value.upper()}")
    
    print_separator()
    print("STEP 9: River Betting Round")
    print_separator()
    
    # Play betting round with random actions
    round_num = 1
    while not game_state.round_complete():
        player = game_state.next_to_act()
        if player is None:
            break
        
        action = player.decide_action(game_state)
        print(f"\n{player.name} {action.type.value.upper()}", end="")
        if action.amount > 0:
            print(f" {action.amount}", end="")
        print()
        
        game_state.execute_action(action)
        print(f"  {player.name}: {player.stack} chips, current bet: {player.current_bet}")
        print(f"  Pot: {pot.get_total()} chips")
        round_num += 1
        
        # Check if hand ended
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            print(f"\n{active_players[0].name} wins by default (opponent folded)!")
            break
    
    print(f"\nBetting round complete!")
    game_state.resolve_bets()
    
    print_separator()
    print("HAND COMPLETE!")
    print_separator()
    
    # Determine winner (simplified - just show who didn't fold)
    active_players = [p for p in game_state.active_players if not p.has_folded]
    if len(active_players) == 1:
        winner = active_players[0]
        print(f"Winner: {winner.name} (opponent folded)")
    else:
        # In a real game, you'd evaluate hands here
        print(f"Showdown! (Hand evaluation not implemented in this demo)")
        print(f"Active players: {[p.name for p in active_players]}")
        winner = active_players[0]  # Simplified - first active player
    
    print(f"Final pot: {pot.get_total()} chips")
    pot.award_to([winner])
    print(f"\nFinal stacks:")
    print(f"  {player1.name}: {player1.stack} chips")
    print(f"  {player2.name}: {player2.stack} chips")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)

if __name__ == "__main__":
    main()

