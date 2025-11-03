from enum import Enum

class Suit(Enum):
	CLUBS = "C"
	DIAMOND = "D"
	HEARTS = "H"
	SPADES = "S"

class Rank(Enum):
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	SIX = 6
	SEVEN = 7
	EIGHT = 8
	NINE = 9
	TEN = 10
	JACK = 11
	QUEEN = 12
	KING = 13
	ACE = 14

class Card:
	def __init__(self, rank: Rank, suit: Suit):
		self.rank = rank
		self.suit = suit
	def __repr__(self):
		return f"{self.rank.value}{self.suit.value}"

card1 = Card(Rank.NINE, Suit.CLUBS)
print(card1)
