
from itertools import product
from core.Card import Card, Rank, Suit
import random

class Deck:
	def __init__(self, seed: int | None = None):
		self.cards = [Card(rank, suit) for suit, rank in product(Suit, Rank)]
		self.rng = random.Random(seed)
	
	def shuffle(self):
		self.rng.shuffle(self.cards)

	def deal_one(self):
		return self.cards.pop() if self.cards else None

	def reset(self):
		self.cards = [Card(rank, suit) for suit, rank in product(Suit, Rank)]
		self.shuffle()

	def __len__(self):
		return len(self.cards)

	def __repr__(self):
		return f"Deck({len(self.cards)} cards)"

if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()
    print(deck.deal_one())
    print(len(deck))

