from src.core.Deck import Deck
from src.core.Table import Table
from src.core.Dealer import Dealer
from src.core.Player import Player
from treys import Evaluator
table = Table()
deck = Deck()
dealer = Dealer(table, deck)
table.dealer = dealer

# add players
table.seats[0].player = Player("Devin", 100)
table.seats[1].player = Player("Echo", 100)
print('Deck size', dealer.deck.__len__())dealer.deal_hole_cards()
print(table.seats[0].player.hand)
print(table.seats[1].player.hand)
print('Deck size', dealer.deck.__len__())dealer.deal_community_cards(3)  # Deal the flop
print(table.community_cards)
print('Deck size', dealer.deck.__len__())dealer.deal_community_cards(1)  # Deal the flop
print(table.community_cards)

print('Deck size', dealer.deck.__len__())dealer.deal_community_cards(1)  # Deal the flop
print(table.community_cards)

print('Deck size', dealer.deck.__len__())