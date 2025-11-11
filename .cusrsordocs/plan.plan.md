<!-- 6775429b-080d-4ff1-b88c-0211f1f2ad2f 06bb969b-13c9-4c05-a174-99ff6fbfb378 -->
# Player Action Selection System Implementation

## Overview

Add the missing components to enable players to choose actions during betting rounds. The system will support both human players (console input) and AI players (programmatic interface).

## Components to Implement

### 1. Action System (`src/core/Action.py`)

- Create `ActionType` enum with: `FOLD`, `CHECK`, `CALL`, `BET`, `RAISE`, `ALL_IN`
- Create `Action` class with attributes: `player`, `type` (ActionType), `amount`
- Add `__str__()` method for display

### 2. Pot Management (`src/core/Pot.py`)

- Create `Pot` class to track betting
- Attributes: `main_pot`, `side_pots` (list), `contributors` (dict mapping player to amount)
- Methods:
- `add_contribution(player, amount)` - add chips to pot
- `resolve_side_pots()` - handle all-in scenarios
- `award_to(winners)` - distribute chips to winners
- `get_total()` - return total pot size

### 3. Game State Management (`src/core/GameState.py`)

- Create `Phase` enum: `PRE_FLOP`, `FLOP`, `TURN`, `RIVER`, `SHOWDOWN`
- Create `GameState` class to manage game flow
- Attributes:
- `phase` (Phase enum)
- `current_bet` (highest bet this round)
- `pot_ref` (Pot instance)
- `active_players` (list of players still in hand)
- `to_act_index` (current player position)
- `table_ref` (Table instance)
- `last_raiser_index` (for betting round completion)
- `min_raise` (minimum raise amount)
- Methods:
- `__init__(table, pot)` - initialize with PRE_FLOP phase
- `next_to_act()` - return next player who needs to act
- `execute_action(action)` - process player action, validate, update state
- `round_complete()` - check if betting round is finished
- `advance_phase()` - move to next phase (flop, turn, river, showdown)
- `resolve_bets()` - finalize bets at end of round
- `get_valid_actions(player)` - return list of valid actions for player
- `get_call_amount(player)` - calculate amount needed to call

### 4. Enhanced Player Class (`src/core/Player.py`)

- Add missing attributes:
- `current_bet` (amount bet this round)
- `is_active` (in current hand)
- `is_all_in` (has gone all-in)
- `has_folded` (has folded)
- `seat_position` (seat number)
- `is_human` (flag for human vs AI)
- Add action methods:
- `post_blind(amount)` - post small/big blind
- `bet(amount)` - place a bet
- `call(amount)` - call current bet
- `fold()` - fold hand
- `check()` - check (no bet)
- `all_in()` - go all-in
- Add decision method:
- `decide_action(game_state)` - get action from player (human input or AI override)
- For human players: prompt console input, validate, return Action
- For AI players: call `get_action(game_state)` method (to be overridden)

### 5. Enhanced Table Class (`src/core/Table.py`)

- Add attributes:
- `pot` (Pot instance)
- `dealer_button` (seat index with button)
- `small_blind` (small blind amount)
- `big_blind` (big blind amount)
- `game_state` (GameState instance, optional)
- Add methods:
- `add_player(player, seat_index)` - add player to specific seat
- `get_next_active_player(current_pos)` - find next active player
- `reset_hand()` - reset for new hand
- `get_active_players()` - return list of active players

### 6. Enhanced Dealer Class (`src/core/Dealer.py`)

- Add methods:
- `rotate_button()` - move dealer button
- `collect_blinds()` - collect small and big blinds from players
- `deal_community(stage)` - deal flop/turn/river with burn cards
- `shuffle_deck()` - shuffle the deck

### 7. Action Validation Logic

- In `GameState.execute_action()`:
- Validate action is legal (check vs call, sufficient chips, min raise rules)
- Update player state (stack, current_bet, flags)
- Update game state (current_bet, pot, turn order)
- Handle all-in scenarios
- Track last raiser for round completion

### 8. Human Input Interface

- In `Player.decide_action()` for human players:
- Display game state (pot, current bet, player's hand, stack)
- Show valid actions
- Prompt for input with validation
- Parse input (e.g., "fold", "call", "bet 50", "raise 100")
- Return Action object

## Implementation Order

1. Create Action and ActionType enum
2. Create Pot class
3. Enhance Player class with state attributes and action methods
4. Enhance Table class with pot and game state support
5. Create GameState class with betting loop logic
6. Enhance Dealer class with blinds and community card methods
7. Implement human input interface in Player.decide_action()
8. Add action validation in GameState.execute_action()

## Files to Create/Modify

- **Create**: `src/core/Action.py`
- **Create**: `src/core/Pot.py`
- **Create**: `src/core/GameState.py`
- **Modify**: `src/core/Player.py` (add attributes, methods, decide_action)
- **Modify**: `src/core/Table.py` (add pot, blinds, game state support)
- **Modify**: `src/core/Dealer.py` (add blinds, button rotation, community cards with burns)

### To-dos

- [x] Create Action.py with ActionType enum and Action class
- [x] Create Pot.py with pot tracking and side pot logic
- [x] Enhance Player.py with state attributes (current_bet, is_active, etc.) and action methods (bet, call, fold, check)
- [x] Enhance Table.py with pot, blinds, dealer_button, and game state support
- [x] Enhance Dealer.py with rotate_button(), collect_blinds(), and deal_community() methods
- [x] Create GameState.py with Phase enum, betting loop logic, action execution, and validation
- [x] Implement human console input interface in Player.decide_action() with game state display and input parsing
- [x] Add comprehensive action validation in GameState.execute_action() (min raise, sufficient chips, legal actions)