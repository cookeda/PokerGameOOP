from src.core.Deck import Deck
from src.core.Table import Table
from src.core.Dealer import Dealer
from src.core.Player import Player
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

table = Table()
deck = Deck()
dealer = Dealer(table, deck)
table.dealer = dealer

# Initialize Treys evaluator
evaluator = Evaluator()

# add players
table.seats[0].player = Player("Devin", 100)
table.seats[1].player = Player("Echo", 100)
print('Deck size', dealer.deck.__len__())
dealer.deal_hole_cards()
print(table.seats[0].player.hand, table.seats[0].player.name)
print(table.seats[1].player.hand, table.seats[1].player.name)
print('Deck size', dealer.deck.__len__())
# Deal flop
dealer.deal_community_cards(3)  # Deal the flop
print(table.community_cards)
print('Deck size', dealer.deck.__len__())  # Check deck size after flop

# Evaluate hands after flop
print("\n--- After Flop ---")
for seat in table.seats:
    if seat.player:
        score, hand_class = evaluate_hand(seat.player, table.community_cards, evaluator)
        if score is not None:
            print(f"{seat.player.name}: Score={score}, Hand={evaluator.class_to_string(hand_class)}")

# Deal turn
dealer.deal_community_cards(1)  # Deal the turn
print(table.community_cards)
print('Deck size', dealer.deck.__len__())  # Check deck size after turn

# Evaluate hands after turn
print("\n--- After Turn ---")
for seat in table.seats:
    if seat.player:
        score, hand_class = evaluate_hand(seat.player, table.community_cards, evaluator)
        if score is not None:
            print(f"{seat.player.name}: Score={score}, Hand={evaluator.class_to_string(hand_class)}")

# Deal river
dealer.deal_community_cards(1)  # Deal the river
print(table.community_cards)
print('Deck size', dealer.deck.__len__())  # Check deck size after river

# Evaluate hands after river
print("\n--- After River ---")
for seat in table.seats:
    if seat.player:
        score, hand_class = evaluate_hand(seat.player, table.community_cards, evaluator)
        if score is not None:
            print(f"{seat.player.name}: Score={score}, Hand={evaluator.class_to_string(hand_class)}")

# Determine winner
print("\n--- Final Results ---")
scores = {}
for seat in table.seats:
    if seat.player:
        score, hand_class = evaluate_hand(seat.player, table.community_cards, evaluator)
        if score is not None:
            scores[seat.player.name] = score
            print(f"{seat.player.name}: Score={score}, Hand={evaluator.class_to_string(hand_class)}")

if scores:
    winner = min(scores, key=scores.get)  # Lower score is better in Treys
    print(f"\nWinner: {winner} (Score: {scores[winner]})")

