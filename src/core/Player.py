from src.core.Action import Action, ActionType

class Player:
    def __init__(self, name, stack, is_human=True):
        self.name = name
        self.stack = stack
        self.hand = []
        # State attributes
        self.current_bet = 0
        self.is_active = True
        self.is_all_in = False
        self.has_folded = False
        self.seat_position = None
        self.is_human = is_human
    
    def reset_hand_state(self):
        """Reset player state for a new hand."""
        self.current_bet = 0
        self.is_active = True
        self.is_all_in = False
        self.has_folded = False
        self.hand = []
    
    def post_blind(self, amount):
        """Post a blind (small or big blind)."""
        if amount > self.stack:
            amount = self.stack
        self.stack -= amount
        self.current_bet = amount
        return amount
    
    def bet(self, amount):
        """Place a bet."""
        if amount > self.stack:
            amount = self.stack
        self.stack -= amount
        self.current_bet += amount
        if self.stack == 0:
            self.is_all_in = True
        return amount
    
    def call(self, amount):
        """Call the current bet."""
        call_amount = min(amount, self.stack)
        self.stack -= call_amount
        self.current_bet += call_amount
        if self.stack == 0:
            self.is_all_in = True
        return call_amount
    
    def fold(self):
        """Fold the hand."""
        self.has_folded = True
        self.is_active = False
    
    def check(self):
        """Check (no bet required)."""
        pass  # No action needed for check
    
    def all_in(self):
        """Go all-in."""
        amount = self.stack
        self.stack = 0
        self.current_bet += amount
        self.is_all_in = True
        return amount
    
    def decide_action(self, game_state):
        """
        Get action from player. For human players, prompts console input.
        For AI players, calls get_action() method (to be overridden).
        """
        if self.is_human:
            return self._get_human_action(game_state)
        else:
            return self.get_action(game_state)
    
    def get_action(self, game_state):
        """
        Override this method for AI players.
        Default implementation raises NotImplementedError.
        """
        raise NotImplementedError("AI players must implement get_action() method")
    
    def _get_human_action(self, game_state):
        """
        Get action from human player via console input.
        Displays game state and prompts for action.
        """
        # Display game state
        print("\n" + "="*60)
        print(f"Player: {self.name}")
        print(f"Stack: {self.stack}")
        print(f"Current Bet: {self.current_bet}")
        print(f"Pot: {game_state.pot.get_total()}")
        print(f"Current Bet to Match: {game_state.current_bet}")
        print(f"Phase: {game_state.phase.value.upper()}")
        print(f"Your Hand: {[str(card) for card in self.hand]}")
        if game_state.table.community_cards:
            print(f"Community Cards: {[str(card) for card in game_state.table.community_cards]}")
        
        # Get valid actions
        valid_actions = game_state.get_valid_actions(self)
        call_amount = game_state.get_call_amount(self)
        
        # Display valid actions
        print("\nValid Actions:")
        action_options = []
        if ActionType.FOLD in valid_actions:
            print("  - fold (or 'f')")
            action_options.append("fold")
            action_options.append("f")
        
        if ActionType.CHECK in valid_actions:
            print("  - check (or 'c')")
            action_options.append("check")
            action_options.append("c")
        
        if ActionType.CALL in valid_actions:
            print(f"  - call {call_amount} (or 'call')")
            action_options.append("call")
        
        if ActionType.BET in valid_actions:
            min_bet = game_state.min_raise
            max_bet = self.stack
            print(f"  - bet <amount> (min: {min_bet}, max: {max_bet})")
            action_options.append("bet")
        
        if ActionType.RAISE in valid_actions:
            min_raise = game_state.current_bet + game_state.min_raise
            max_raise = self.stack + self.current_bet
            print(f"  - raise <amount> (min: {min_raise}, max: {max_raise})")
            action_options.append("raise")
        
        if ActionType.ALL_IN in valid_actions:
            print(f"  - all-in (or 'allin' or 'ai') - {self.stack}")
            action_options.append("all-in")
            action_options.append("allin")
            action_options.append("ai")
        
        # Get user input
        while True:
            try:
                user_input = input(f"\n{self.name}, choose your action: ").strip().lower()
                
                if not user_input:
                    print("Please enter an action.")
                    continue
                
                # Parse input
                parts = user_input.split()
                action_word = parts[0]
                amount = None
                if len(parts) > 1:
                    try:
                        amount = int(parts[1])
                    except ValueError:
                        print(f"Invalid amount: {parts[1]}")
                        continue
                
                # Handle fold
                if action_word in ["fold", "f"]:
                    if ActionType.FOLD not in valid_actions:
                        print("Cannot fold at this time.")
                        continue
                    return Action(self, ActionType.FOLD)
                
                # Handle check
                elif action_word in ["check", "c"]:
                    if ActionType.CHECK not in valid_actions:
                        print("Cannot check at this time.")
                        continue
                    return Action(self, ActionType.CHECK)
                
                # Handle call
                elif action_word == "call":
                    if ActionType.CALL not in valid_actions:
                        print("Cannot call at this time.")
                        continue
                    return Action(self, ActionType.CALL, call_amount)
                
                # Handle bet
                elif action_word == "bet":
                    if ActionType.BET not in valid_actions:
                        print("Cannot bet at this time.")
                        continue
                    if amount is None:
                        print("Please specify bet amount: bet <amount>")
                        continue
                    if amount < game_state.min_raise:
                        print(f"Bet must be at least {game_state.min_raise}")
                        continue
                    if amount > self.stack:
                        print(f"Cannot bet more than your stack ({self.stack})")
                        continue
                    return Action(self, ActionType.BET, amount)
                
                # Handle raise
                elif action_word == "raise":
                    if ActionType.RAISE not in valid_actions:
                        print("Cannot raise at this time.")
                        continue
                    if amount is None:
                        print("Please specify raise amount: raise <amount>")
                        continue
                    min_raise_total = game_state.current_bet + game_state.min_raise
                    if amount < min_raise_total:
                        print(f"Raise must be at least {min_raise_total}")
                        continue
                    max_raise_total = self.stack + self.current_bet
                    if amount > max_raise_total:
                        print(f"Cannot raise more than available ({max_raise_total})")
                        continue
                    return Action(self, ActionType.RAISE, amount)
                
                # Handle all-in
                elif action_word in ["all-in", "allin", "ai"]:
                    if ActionType.ALL_IN not in valid_actions:
                        print("Cannot go all-in at this time.")
                        continue
                    return Action(self, ActionType.ALL_IN, self.stack)
                
                else:
                    print(f"Unknown action: {action_word}")
                    print(f"Valid actions: {', '.join(set(action_options))}")
                    continue
                    
            except KeyboardInterrupt:
                print("\nAction cancelled. Folding...")
                return Action(self, ActionType.FOLD)
            except Exception as e:
                print(f"Error: {e}")
                continue