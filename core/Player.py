
class Player:
    def __init__(self, player_id: int, name: str, stack: int, current_bet: int, is_folded: bool):
        pass

    def bet(self, amount: int):
        pass

    def call(self, to_call: bool):
        pass

    def raise_to(self, amount: int):
        pass

    def fold(self):
        pass

    def reset_for_hand(self):
        #FIXME: What is this even for?
        pass

