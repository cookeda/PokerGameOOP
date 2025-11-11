from src.core.Deck import Deck
from src.core.Table import Table

class Dealer:
    def __init__(self, table: Table, deck: Deck):
        self.table = table
        self.deck = deck
        self.deck.shuffle()
        
    def shuffle_deck(self):
        """Shuffle the deck."""
        self.deck.shuffle()
    
    def deal_card(self, player):
        """Deal one card to a player."""
        card = self.deck.deal_one()
        if card:
            player.hand.append(card)
        
    def deal_hole_cards(self):
        """Deal two hole cards to each active player."""
        for _ in range(2):
            for seat in self.table.seats:
                if seat.player and seat.player.is_active:
                    self.deal_card(seat.player)

    def deal_community_cards(self, n: int):
        """Deal n community cards (with burn card)."""
        # Burn one card
        self.deck.deal_one()
        # Deal n cards
        for _ in range(n):
            card = self.deck.deal_one()
            if card:
                self.table.community_cards.append(card)
    
    def deal_community(self, stage: str):
        """
        Deal community cards for a specific stage (FLOP, TURN, RIVER).
        Always burns one card before dealing.
        """
        # Burn one card
        self.deck.deal_one()
        
        if stage.upper() == "FLOP":
            # Deal 3 cards for flop
            for _ in range(3):
                card = self.deck.deal_one()
                if card:
                    self.table.community_cards.append(card)
        elif stage.upper() in ["TURN", "RIVER"]:
            # Deal 1 card for turn or river
            card = self.deck.deal_one()
            if card:
                self.table.community_cards.append(card)
        else:
            raise ValueError(f"Invalid stage: {stage}. Must be FLOP, TURN, or RIVER")
    
    def rotate_button(self):
        """Move the dealer button to the next active player."""
        n_seats = len(self.table.seats)
        # Find next seat with an active player
        for i in range(1, n_seats):
            next_pos = (self.table.dealer_button + i) % n_seats
            seat = self.table.seats[next_pos]
            if seat.player and seat.player.stack > 0:
                self.table.dealer_button = next_pos
                return
        # If no active players found, just move button
        self.table.dealer_button = (self.table.dealer_button + 1) % n_seats
    
    def collect_blinds(self):
        """
        Collect small blind and big blind from players.
        Small blind is left of button, big blind is left of small blind.
        """
        n_seats = len(self.table.seats)
        sb_pos = (self.table.dealer_button + 1) % n_seats
        bb_pos = (self.table.dealer_button + 2) % n_seats
        
        # Collect small blind
        sb_seat = self.table.seats[sb_pos]
        if sb_seat.player and sb_seat.player.is_active:
            sb_amount = sb_seat.player.post_blind(self.table.small_blind)
            self.table.pot.add_contribution(sb_seat.player, sb_amount)
        
        # Collect big blind
        bb_seat = self.table.seats[bb_pos]
        if bb_seat.player and bb_seat.player.is_active:
            bb_amount = bb_seat.player.post_blind(self.table.big_blind)
            self.table.pot.add_contribution(bb_seat.player, bb_amount)
            return bb_amount  # Return big blind amount as current bet
        
        return 0
