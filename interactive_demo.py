"""
Interactive poker demo where a human player plays against random AI bots.
Uses treys library for hand evaluation at showdown.
"""
import random
from src.core.Deck import Deck
from src.core.Table import Table
from src.core.Dealer import Dealer
from src.core.Player import Player
from src.core.Pot import Pot
from src.core.GameState import GameState, Phase
from src.core.Action import Action, ActionType
from src.core.Card import Card, Suit, Rank
from treys import Card as TreysCard, Evaluator


def card_to_treys(card: Card) -> int:
    """Convert a Card object to Treys format using Card.new().
    
    Treys format: string like 'Ah' (Ace of Hearts)
    - Rank: '2'-'9', 'T' (10), 'J', 'Q', 'K', 'A'
    - Suit: 'c' (clubs), 'd' (diamonds), 'h' (hearts), 's' (spades)
    """
    # Map rank to string
    rank_map = {
        2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'
    }
    
    # Map suit to string
    suit_map = {
        Suit.CLUBS: 'c',
        Suit.DIAMOND: 'd',
        Suit.HEARTS: 'h',
        Suit.SPADES: 's'
    }
    
    rank_str = rank_map[card.rank.value]
    suit_str = suit_map[card.suit]
    
    return TreysCard.new(rank_str + suit_str)


def evaluate_hand(player: Player, community_cards: list, evaluator: Evaluator):
    """Evaluate a player's hand using Treys evaluator."""
    if not player.hand or len(player.hand) < 2:
        return None, None
    
    # Convert cards to Treys format
    hole_cards = [card_to_treys(card) for card in player.hand]
    board = [card_to_treys(card) for card in community_cards]
    
    # Evaluate the hand (note: evaluator.evaluate takes board first, then hole_cards)
    score = evaluator.evaluate(board, hole_cards)
    hand_class = evaluator.get_rank_class(score)
    
    return score, hand_class


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


def print_separator():
    """Print a visual separator."""
    print("\n" + "="*60 + "\n")


def print_game_state(game_state, human_player):
    """Print current game state information."""
    print_separator()
    print(f"PHASE: {game_state.phase.value.upper().replace('_', '-')}")
    print_separator()
    print(f"Pot: {game_state.pot.get_total()} chips")
    print(f"Current bet to match: {game_state.current_bet}")
    if game_state.table.community_cards:
        print(f"Community cards: {[str(card) for card in game_state.table.community_cards]}")
    print("\nPlayer stacks:")
    for seat in game_state.table.seats:
        if seat.player:
            status = ""
            if seat.player.has_folded:
                status = " [FOLDED]"
            elif seat.player.is_all_in:
                status = " [ALL-IN]"
            print(f"  {seat.player.name}: {seat.player.stack} chips{status}")
    print(f"\nYour hand: {[str(card) for card in human_player.hand]}")


def play_betting_round(game_state, human_player, evaluator):
    """Play a complete betting round."""
    while not game_state.round_complete():
        player = game_state.next_to_act()
        if player is None:
            break
        
        # Check if hand ended early (only one player left)
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) <= 1:
            break
        
        # Show game state before human player acts
        if player.is_human:
            print_game_state(game_state, human_player)
        
        # Get action from player
        action = player.decide_action(game_state)
        
        # Display action
        if player.is_human:
            print(f"\n{player.name} {action.type.value.upper()}", end="")
            if action.amount > 0:
                print(f" {action.amount}", end="")
            print()
        else:
            print(f"{player.name} {action.type.value.upper()}", end="")
            if action.amount > 0:
                print(f" {action.amount}", end="")
            print()
        
        # Execute action
        game_state.execute_action(action)
        
        # Check if hand ended (only one player left)
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) <= 1:
            break
    
    # Resolve bets at end of round
    game_state.resolve_bets()
    return len([p for p in game_state.active_players if not p.has_folded])


def handle_showdown(game_state, evaluator):
    """Handle showdown phase with hand evaluation using treys."""
    print_separator()
    print("SHOWDOWN!")
    print_separator()
    
    active_players = [p for p in game_state.active_players if not p.has_folded]
    
    if len(active_players) == 0:
        print("No active players for showdown!")
        return []
    
    # Evaluate all hands
    player_scores = {}
    for player in active_players:
        score, hand_class = evaluate_hand(player, game_state.table.community_cards, evaluator)
        if score is not None:
            player_scores[player] = score
            hand_name = evaluator.class_to_string(hand_class)
            print(f"{player.name}: {[str(card) for card in player.hand]} - {hand_name} (score: {score})")
    
    if not player_scores:
        print("No valid hands to evaluate!")
        return []
    
    # Find winner(s) - lower score is better in Treys
    best_score = min(player_scores.values())
    winners = [player for player, score in player_scores.items() if score == best_score]
    
    print_separator()
    if len(winners) == 1:
        winner = winners[0]
        winner_score = player_scores[winner]
        winner_hand = evaluator.class_to_string(evaluator.get_rank_class(winner_score))
        print(f"Winner: {winner.name} with {winner_hand}!")
    else:
        print(f"Tie! Winners: {', '.join([w.name for w in winners])}")
    
    return winners


def play_hand(table, dealer, pot, human_player, evaluator):
    """Play a single hand of poker."""
    print_separator()
    print("="*60)
    print("NEW HAND")
    print("="*60)
    print_separator()
    
    # Reset table for new hand
    table.reset_hand()
    
    # Collect blinds
    print("Collecting blinds...")
    dealer.collect_blinds()
    print(f"Small blind ({table.small_blind}) and big blind ({table.big_blind}) posted")
    
    # Create game state
    game_state = GameState(table, pot)
    game_state.current_bet = table.big_blind
    
    # Deal hole cards
    print_separator()
    print("Dealing hole cards...")
    dealer.deal_hole_cards()
    print(f"Your hand: {[str(card) for card in human_player.hand]}")
    
    # Pre-flop betting round
    print_separator()
    print("PRE-FLOP BETTING ROUND")
    print_separator()
    remaining_players = play_betting_round(game_state, human_player, evaluator)
    
    # Check if hand ended early
    if remaining_players <= 1:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print_separator()
            print(f"{winner.name} wins! (All other players folded)")
            pot.award_to([winner])
            return
        else:
            print("Error: No active players remaining")
            return
    
    # Flop
    print_separator()
    print("Dealing the FLOP...")
    game_state.advance_phase()
    print(f"Community cards: {[str(card) for card in table.community_cards]}")
    
    # Flop betting round
    print_separator()
    print("FLOP BETTING ROUND")
    print_separator()
    remaining_players = play_betting_round(game_state, human_player, evaluator)
    
    if remaining_players <= 1:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print_separator()
            print(f"{winner.name} wins! (All other players folded)")
            pot.award_to([winner])
            return
    
    # Turn
    print_separator()
    print("Dealing the TURN...")
    game_state.advance_phase()
    print(f"Community cards: {[str(card) for card in table.community_cards]}")
    
    # Turn betting round
    print_separator()
    print("TURN BETTING ROUND")
    print_separator()
    remaining_players = play_betting_round(game_state, human_player, evaluator)
    
    if remaining_players <= 1:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print_separator()
            print(f"{winner.name} wins! (All other players folded)")
            pot.award_to([winner])
            return
    
    # River
    print_separator()
    print("Dealing the RIVER...")
    game_state.advance_phase()
    print(f"Community cards: {[str(card) for card in table.community_cards]}")
    
    # River betting round
    print_separator()
    print("RIVER BETTING ROUND")
    print_separator()
    remaining_players = play_betting_round(game_state, human_player, evaluator)
    
    if remaining_players <= 1:
        active_players = [p for p in game_state.active_players if not p.has_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print_separator()
            print(f"{winner.name} wins! (All other players folded)")
            pot.award_to([winner])
            return
    
    # Showdown
    game_state.advance_phase()
    winners = handle_showdown(game_state, evaluator)
    
    if winners:
        pot.award_to(winners)
        print(f"Pot awarded: {pot.get_total()} chips")
    else:
        print("No winners determined!")


def main():
    """Main game loop."""
    print("="*60)
    print("INTERACTIVE POKER GAME")
    print("Play against random AI bots!")
    print("="*60)
    
    # Get player name
    player_name = input("\nEnter your name: ").strip()
    if not player_name:
        player_name = "Player"
    
    # Initialize game components
    table = Table(n_seats=6, small_blind=1, big_blind=2)
    deck = Deck()
    dealer = Dealer(table, deck)
    table.dealer = dealer
    pot = Pot()
    evaluator = Evaluator()
    
    # Create players
    human_player = Player(player_name, 100, is_human=True)
    bot1 = RandomAIPlayer("Bot1", 100, is_human=False)
    bot2 = RandomAIPlayer("Bot2", 100, is_human=False)
    
    # Add players to table
    table.add_player(human_player, seat_index=0)
    table.add_player(bot1, seat_index=1)
    table.add_player(bot2, seat_index=2)
    
    print(f"\nPlayers:")
    print(f"  {human_player.name}: {human_player.stack} chips")
    print(f"  {bot1.name}: {bot1.stack} chips")
    print(f"  {bot2.name}: {bot2.stack} chips")
    
    # Main game loop
    hand_number = 1
    while True:
        # Check if any player is eliminated
        active_players = [p for p in [human_player, bot1, bot2] if p.stack > 0]
        if len(active_players) < 2:
            print_separator()
            print("GAME OVER!")
            if human_player.stack > 0:
                print(f"Congratulations {human_player.name}! You won!")
            else:
                print(f"Game over! You've been eliminated.")
            break
        
        # Play a hand
        play_hand(table, dealer, pot, human_player, evaluator)
        
        # Show final stacks
        print_separator()
        print("Stacks after hand:")
        print(f"  {human_player.name}: {human_player.stack} chips")
        print(f"  {bot1.name}: {bot1.stack} chips")
        print(f"  {bot2.name}: {bot2.stack} chips")
        
        # Check if human player is out
        if human_player.stack <= 0:
            print_separator()
            print("You're out of chips! Game over.")
            break
        
        # Rotate button
        dealer.rotate_button()
        
        # Shuffle deck for next hand
        dealer.shuffle_deck()
        
        # Ask to continue
        print_separator()
        response = input("Play another hand? (y/n): ").strip().lower()
        if response != 'y' and response != 'yes':
            print("\nThanks for playing!")
            break
        
        hand_number += 1
    
    # Final summary
    print_separator()
    print("FINAL RESULTS:")
    print(f"  {human_player.name}: {human_player.stack} chips")
    print(f"  {bot1.name}: {bot1.stack} chips")
    print(f"  {bot2.name}: {bot2.stack} chips")
    print("="*60)


if __name__ == "__main__":
    main()

