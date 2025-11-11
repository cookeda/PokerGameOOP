"""
Interactive demo script allowing human players to play poker hands.
"""
import random
import os
from src.core.Deck import Deck
from src.core.Table import Table
from src.core.Dealer import Dealer
from src.core.Player import Player
from src.core.Pot import Pot
from src.core.GameState import GameState, Phase
from src.core.Action import Action, ActionType


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


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_separator(char="=", width=70):
    """Print a visual separator line."""
    print("\n" + char * width + "\n")


def display_game_state(game_state, human_player):
    """
    Display the current game state in a clear, organized format.
    Only shows human player's cards; hides opponent cards until showdown.
    """
    table = game_state.table
    pot = game_state.pot
    
    print_separator()
    print(f"PHASE: {game_state.phase.value.upper().replace('_', '-')}")
    print_separator("-", 70)
    
    # Display dealer button and blinds
    print(f"Dealer Button: Seat {table.dealer_button}")
    print(f"Blinds: {table.small_blind}/{table.big_blind}")
    print()
    
    # Display community cards
    if table.community_cards:
        print("Community Cards:")
        print(f"  {[str(card) for card in table.community_cards]}")
    else:
        print("Community Cards: (none yet)")
    print()
    
    # Display pot and current bet
    print(f"Pot: {pot.get_total()} chips")
    print(f"Current Bet to Match: {game_state.current_bet} chips")
    print()
    
    # Display all players
    print("Players:")
    for i, seat in enumerate(table.seats):
        if seat.player:
            player = seat.player
            is_dealer = (i == table.dealer_button)
            is_sb = (i == (table.dealer_button + 1) % len(table.seats))
            is_bb = (i == (table.dealer_button + 2) % len(table.seats))
            
            # Build position indicator
            position = []
            if is_dealer:
                position.append("D")
            if is_sb:
                position.append("SB")
            if is_bb:
                position.append("BB")
            position_str = f" [{', '.join(position)}]" if position else ""
            
            # Show cards only for human player or if hand is over
            if player == human_player:
                cards_str = f"Hand: {[str(card) for card in player.hand]}"
            else:
                if player.has_folded:
                    cards_str = "Hand: [FOLDED]"
                elif game_state.phase == Phase.SHOWDOWN:
                    cards_str = f"Hand: {[str(card) for card in player.hand]}"
                else:
                    cards_str = "Hand: [??]"
            
            status_parts = []
            if player.has_folded:
                status_parts.append("FOLDED")
            if player.is_all_in:
                status_parts.append("ALL-IN")
            status_str = f" ({', '.join(status_parts)})" if status_parts else ""
            
            print(f"  Seat {i}: {player.name}{position_str}")
            print(f"    Stack: {player.stack} chips | Current Bet: {player.current_bet} chips")
            print(f"    {cards_str}{status_str}")
    
    print_separator("-", 70)


def play_interactive_betting_round(game_state, round_name, human_player, max_actions=50):
    """
    Play a complete betting round with interactive prompts for human players.
    
    Args:
        game_state: The current GameState object
        round_name: Name of the betting round (for display)
        human_player: The human player object
        max_actions: Maximum number of actions to prevent infinite loops
    
    Returns:
        tuple: (hand_ended: bool, action_count: int)
        - hand_ended: True if hand ended early (only one player remains), False otherwise
        - action_count: Number of actions taken in this round
    """
    action_count = 0
    hand_ended = False
    
    while not game_state.round_complete() and action_count < max_actions:
        player = game_state.next_to_act()
        if player is None:
            # If next_to_act() returns None but round isn't complete, there's a state issue
            break
        
        # Clear screen and show game state before each action
        if player == human_player:
            clear_screen()
            display_game_state(game_state, human_player)
            print(f"\n>>> It's your turn, {player.name}! <<<")
        else:
            # For AI players, just show a brief message
            print(f"\n{player.name} is thinking...")
        
        # Get action from player
        action = player.decide_action(game_state)
        action_count += 1
        
        # Display the action
        if player == human_player:
            print(f"\nYou chose: {action.type.value.upper()}", end="")
        else:
            print(f"{player.name} {action.type.value.upper()}", end="")
        
        if action.amount > 0:
            print(f" {action.amount} chips", end="")
        print()
        
        # Execute the action
        game_state.execute_action(action)
        
        # Show updated state
        if player == human_player:
            print(f"  Your stack: {player.stack} chips | Your bet: {player.current_bet} chips")
        else:
            print(f"  {player.name}: {player.stack} chips, current bet: {player.current_bet} chips")
        
        print(f"  Pot: {game_state.pot.get_total()} chips")
        print(f"  Current bet to match: {game_state.current_bet} chips")
        
        # Check if hand ended (only one player remains)
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n>>> {winner.name} wins by default (all opponents folded)! <<<")
            hand_ended = True
            break
        
        # Small pause for AI actions to make it more readable
        if player != human_player:
            import time
            time.sleep(0.5)
    
    if not hand_ended:
        print(f"\n--- {round_name} Betting Round Complete ({action_count} actions) ---")
    
    return hand_ended, action_count


def play_hand(table, dealer, pot, human_player):
    """
    Play a complete poker hand from start to finish.
    
    Returns:
        tuple: (winner: Player, hand_ended_early: bool)
    """
    # Reset hand state
    table.reset_hand()
    dealer.shuffle_deck()
    dealer.rotate_button()
    
    # Collect blinds
    clear_screen()
    print_separator()
    print("NEW HAND - Collecting Blinds")
    print_separator()
    dealer.collect_blinds()
    
    # Display initial state
    display_game_state(GameState(table, pot), human_player)
    input("\nPress Enter to continue...")
    
    # Deal hole cards
    clear_screen()
    print_separator()
    print("Dealing Hole Cards")
    print_separator()
    dealer.deal_hole_cards()
    
    # Show human player their cards
    display_game_state(GameState(table, pot), human_player)
    print(f"\n>>> You received: {[str(card) for card in human_player.hand]} <<<")
    input("\nPress Enter to start Pre-Flop betting...")
    
    # Pre-Flop betting round
    game_state = GameState(table, pot)
    game_state.current_bet = table.big_blind  # Big blind is the initial bet to match
    
    hand_ended, _ = play_interactive_betting_round(game_state, "Pre-Flop", human_player)
    if not hand_ended:
        game_state.resolve_bets()
    
    if hand_ended:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        return active_players[0], True
    
    # Flop
    clear_screen()
    print_separator()
    print("Dealing the Flop")
    print_separator()
    game_state.advance_phase()
    display_game_state(game_state, human_player)
    input("\nPress Enter to start Flop betting...")
    
    hand_ended, _ = play_interactive_betting_round(game_state, "Flop", human_player)
    if not hand_ended:
        game_state.resolve_bets()
    
    if hand_ended:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        return active_players[0], True
    
    # Turn
    clear_screen()
    print_separator()
    print("Dealing the Turn")
    print_separator()
    game_state.advance_phase()
    display_game_state(game_state, human_player)
    input("\nPress Enter to start Turn betting...")
    
    hand_ended, _ = play_interactive_betting_round(game_state, "Turn", human_player)
    if not hand_ended:
        game_state.resolve_bets()
    
    if hand_ended:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        return active_players[0], True
    
    # River
    clear_screen()
    print_separator()
    print("Dealing the River")
    print_separator()
    game_state.advance_phase()
    display_game_state(game_state, human_player)
    input("\nPress Enter to start River betting...")
    
    hand_ended, _ = play_interactive_betting_round(game_state, "River", human_player)
    if not hand_ended:
        game_state.resolve_bets()
    
    # Showdown
    clear_screen()
    print_separator()
    print("SHOWDOWN")
    print_separator()
    game_state.advance_phase()  # Advances to SHOWDOWN phase
    display_game_state(game_state, human_player)  # Now shows all cards
    
    # Determine winner (simplified - first active player wins)
    # In a real implementation, you'd evaluate hands here
    active_players = [p for p in game_state.active_players if not p.has_folded]
    if len(active_players) == 1:
        return active_players[0], False
    else:
        # For now, just pick the first active player
        # TODO: Implement proper hand evaluation
        print("\nNote: Hand evaluation not fully implemented. Winner selected arbitrarily.")
        return active_players[0], False


def display_hand_results(winner, pot, all_players, hand_ended_early):
    """Display the results of a completed hand."""
    print_separator()
    if hand_ended_early:
        print("HAND ENDED EARLY")
    else:
        print("HAND COMPLETE - SHOWDOWN")
    print_separator()
    
    print(f"Winner: {winner.name}")
    print(f"Pot Awarded: {pot.get_total()} chips")
    
    # Award the pot
    pot.award_to([winner])
    
    print("\nFinal Stacks:")
    for player in all_players:
        print(f"  {player.name}: {player.stack} chips")
    
    print_separator()


def main():
    """Main function to run the interactive poker demo."""
    print("="*70)
    print("INTERACTIVE POKER GAME DEMO")
    print("="*70)
    
    # Get human player name
    human_name = input("\nEnter your name: ").strip()
    if not human_name:
        human_name = "Player"
    
    # Configuration
    starting_stack = 100
    small_blind = 1
    big_blind = 2
    n_ai_players = 2  # Number of AI opponents
    
    # Create table
    table = Table(n_seats=6, small_blind=small_blind, big_blind=big_blind)
    deck = Deck()
    dealer = Dealer(table, deck)
    table.dealer = dealer
    pot = Pot()
    
    # Create human player
    human_player = Player(human_name, starting_stack, is_human=True)
    table.add_player(human_player, seat_index=0)
    
    # Create AI opponents
    ai_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    ai_players = []
    for i in range(n_ai_players):
        ai_player = RandomAIPlayer(ai_names[i], starting_stack, is_human=False)
        table.add_player(ai_player, seat_index=i+1)
        ai_players.append(ai_player)
    
    all_players = [human_player] + ai_players
    
    print(f"\nGame Setup:")
    print(f"  Players: {human_name} (You) + {', '.join([p.name for p in ai_players])}")
    print(f"  Starting Stack: {starting_stack} chips per player")
    print(f"  Blinds: {small_blind}/{big_blind}")
    input("\nPress Enter to start the first hand...")
    
    # Play hands until user quits or someone is out
    hand_number = 1
    while True:
        # Check if anyone is out
        active_count = sum(1 for p in all_players if p.stack > 0)
        if active_count < 2:
            print("\nNot enough players with chips to continue!")
            break
        
        # Play a hand
        winner, hand_ended_early = play_hand(table, dealer, pot, human_player)
        
        # Show results
        clear_screen()
        display_hand_results(winner, pot, all_players, hand_ended_early)
        
        # Check if human player is out
        if human_player.stack <= 0:
            print(f"\n{human_name}, you're out of chips! Game over.")
            break
        
        # Ask if user wants to continue
        print()
        response = input("Play another hand? (y/n): ").strip().lower()
        if response != 'y' and response != 'yes':
            break
        
        hand_number += 1
    
    # Final summary
    print_separator()
    print("GAME SESSION ENDED")
    print_separator()
    print("Final Stacks:")
    for player in all_players:
        print(f"  {player.name}: {player.stack} chips")
    print("\nThanks for playing!")
    print("="*70)


if __name__ == "__main__":
    main()

