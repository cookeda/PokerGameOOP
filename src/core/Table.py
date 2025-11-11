from src.core.Seat import Seat
from src.core.Pot import Pot

class Table:
    def __init__(self, n_seats=6, small_blind=1, big_blind=2):
        self.seats = [Seat(i) for i in range(n_seats)]
        self.community_cards = []
        self.dealer = None
        self.pot = Pot()
        self.dealer_button = 0
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.game_state = None
    
    def add_player(self, player, seat_index=None):
        """Add a player to the table at a specific seat or first available seat."""
        if seat_index is None:
            # Find first available seat
            for seat in self.seats:
                if seat.player is None:
                    seat.player = player
                    player.seat_position = seat.seat_id
                    return seat.seat_id
            raise ValueError("No available seats")
        else:
            if seat_index < 0 or seat_index >= len(self.seats):
                raise ValueError(f"Invalid seat index: {seat_index}")
            if self.seats[seat_index].player is not None:
                raise ValueError(f"Seat {seat_index} is already occupied")
            self.seats[seat_index].player = player
            player.seat_position = seat_index
            return seat_index
    
    def remove_player(self, player):
        """Remove a player from the table."""
        for seat in self.seats:
            if seat.player == player:
                seat.player = None
                player.seat_position = None
                return
        raise ValueError(f"Player {player.name} not found at table")
    
    def get_active_players(self):
        """Return list of players who are active in the current hand."""
        active = []
        for seat in self.seats:
            if seat.player and seat.player.is_active and not seat.player.has_folded:
                active.append(seat.player)
        return active
    
    def get_next_active_player(self, current_pos):
        """
        Find the next active player after current_pos.
        Returns (player, seat_index) or (None, None) if no active players found.
        """
        n_seats = len(self.seats)
        for i in range(1, n_seats):
            next_pos = (current_pos + i) % n_seats
            seat = self.seats[next_pos]
            if seat.player and seat.player.is_active and not seat.player.has_folded and not seat.player.is_all_in:
                return seat.player, next_pos
        return None, None
    
    def reset_hand(self):
        """Reset the table for a new hand."""
        self.community_cards = []
        self.pot.reset()
        for seat in self.seats:
            if seat.player:
                seat.player.reset_hand_state()