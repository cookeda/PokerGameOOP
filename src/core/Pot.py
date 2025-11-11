class Pot:
    def __init__(self):
        self.main_pot = 0
        self.side_pots = []  # List of dicts: [{"amount": int, "contributors": set}]
        self.contributors = {}  # Dict mapping player to total amount contributed
    
    def add_contribution(self, player, amount):
        """Add chips from a player to the pot."""
        if amount > 0:
            self.main_pot += amount
            if player not in self.contributors:
                self.contributors[player] = 0
            self.contributors[player] += amount
    
    def get_total(self):
        """Return the total pot size including side pots."""
        total = self.main_pot
        for side_pot in self.side_pots:
            total += side_pot.get("amount", 0)
        return total
    
    def resolve_side_pots(self):
        """
        Resolve side pots when players go all-in.
        This creates separate pots for different all-in amounts.
        """
        if not self.contributors:
            return
        
        # Get all unique contribution amounts, sorted ascending
        amounts = sorted(set(self.contributors.values()))
        
        if len(amounts) <= 1:
            # No side pots needed
            return
        
        # Create side pots from smallest to largest
        self.side_pots = []
        previous_amount = 0
        
        for amount in amounts[:-1]:  # All except the largest
            side_pot_amount = 0
            contributors = set()
            
            # Calculate how much goes into this side pot
            for player, player_contribution in self.contributors.items():
                if player_contribution >= amount:
                    contribution_to_side_pot = amount - previous_amount
                    side_pot_amount += contribution_to_side_pot
                    contributors.add(player)
            
            if side_pot_amount > 0:
                self.side_pots.append({
                    "amount": side_pot_amount,
                    "contributors": contributors
                })
            
            previous_amount = amount
        
        # Adjust main pot - subtract all side pot amounts
        side_pot_total = sum(sp["amount"] for sp in self.side_pots)
        self.main_pot -= side_pot_total
    
    def award_to(self, winners):
        """
        Award pot(s) to winner(s).
        winners: list of Player objects or dict mapping pot to winners
        """
        if isinstance(winners, list):
            # Simple case: award main pot to winners
            if winners:
                amount_per_winner = self.main_pot // len(winners)
                remainder = self.main_pot % len(winners)
                
                for winner in winners:
                    winner.stack += amount_per_winner
                    if remainder > 0:
                        winner.stack += 1
                        remainder -= 1
                # Clear main pot after awarding
                self.main_pot = 0
        else:
            # Complex case: award different pots to different winners
            # winners should be a dict: {pot_index: [Player, ...]}
            # Award main pot
            if "main" in winners and winners["main"]:
                main_winners = winners["main"]
                amount_per_winner = self.main_pot // len(main_winners)
                remainder = self.main_pot % len(main_winners)
                
                for winner in main_winners:
                    winner.stack += amount_per_winner
                    if remainder > 0:
                        winner.stack += 1
                        remainder -= 1
                # Clear main pot after awarding
                self.main_pot = 0
            
            # Award side pots
            for i, side_pot in enumerate(self.side_pots):
                if i in winners and winners[i]:
                    side_winners = winners[i]
                    amount_per_winner = side_pot["amount"] // len(side_winners)
                    remainder = side_pot["amount"] % len(side_winners)
                    
                    for winner in side_winners:
                        winner.stack += amount_per_winner
                        if remainder > 0:
                            winner.stack += 1
                            remainder -= 1
                    # Clear side pot after awarding
                    side_pot["amount"] = 0
    
    def reset(self):
        """Reset the pot for a new hand."""
        self.main_pot = 0
        self.side_pots = []
        self.contributors = {}

