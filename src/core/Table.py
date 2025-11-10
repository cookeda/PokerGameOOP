from src.core.Seat import Seat

class Table:
    def __init__(self, n_seats=6):
        self.seats = [Seat(i) for i in range(n_seats)]
        self.community_cards = []
        self.dealer = None