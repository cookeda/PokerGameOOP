from src.core.Deck import Deck
from src.core.Table import Table

class Dealer:
    def __init__(self, table: Table, deck: Deck):
        self.table = table
        self.deck = deck
        self.deck.shuffle()
        
    def deal_card(self, player):
        player.hand.append(self.deck.deal_one())
        
    def deal_hole_cards(self):
        for _ in range(2):
            for seat in self.table.seats:
                if seat.player:
                    self.deal_card(seat.player)

    def deal_community_cards(self, n: int):
        self.deck.deal_one
        for _ in range(n):
            card = self.deck.deal_one()
            if card:
                self.table.community_cards.append(card)
