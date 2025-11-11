from enum import Enum

class ActionType(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"

class Action:
    def __init__(self, player, action_type: ActionType, amount: int = 0):
        self.player = player
        self.type = action_type
        self.amount = amount
    
    def __str__(self):
        if self.type == ActionType.FOLD:
            return f"{self.player.name} folds"
        elif self.type == ActionType.CHECK:
            return f"{self.player.name} checks"
        elif self.type == ActionType.CALL:
            return f"{self.player.name} calls {self.amount}"
        elif self.type == ActionType.BET:
            return f"{self.player.name} bets {self.amount}"
        elif self.type == ActionType.RAISE:
            return f"{self.player.name} raises to {self.amount}"
        elif self.type == ActionType.ALL_IN:
            return f"{self.player.name} goes all-in with {self.amount}"
        return f"{self.player.name} {self.type.value} {self.amount}"
    
    def __repr__(self):
        return f"Action({self.player.name}, {self.type.value}, {self.amount})"

