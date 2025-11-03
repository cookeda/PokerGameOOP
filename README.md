
## 1. Core Objects

### **1.1 Card**

Represents a single playing card.

* **Attributes:** `rank`, `suit`, `value`, `repr`.
* **Methods:** `__str__()`, `__lt__()` for comparisons.

### **1.2 Deck**

Manages the set of 52 cards.

* **Attributes:** `cards`, `seed`.
* **Methods:**

  * `shuffle()`: randomize order.
  * `deal_one()`: pops a card.
  * `reset()`: rebuilds a full deck.

### **1.3 Player**

Models a seat occupant.

* **Attributes:**

  * `id`, `name`
  * `stack` (chips)
  * `hand` (list of 2 cards)
  * `current_bet`
  * `is_active`, `is_all_in`, `has_folded`, `seat_position`
* **Methods:**

  * `post_blind(amount)`
  * `bet(amount)`
  * `call(amount)`
  * `fold()`
  * `check()`
  * `decide_action(game_state)` → returns action object.

### **1.4 Dealer**

Encapsulates dealing logic and button rotation.

* **Attributes:** `table_ref`, `deck`.
* **Methods:**

  * `rotate_button()`
  * `deal_hole_cards()`
  * `deal_community(stage)` → handles flop, turn, river.
  * `collect_blinds()`.

### **1.5 Pot**

Tracks the chips bet in the hand.

* **Attributes:**

  * `main_pot`, `side_pots`, `contributors`.
* **Methods:**

  * `add_contribution(player, amount)`
  * `resolve_side_pots()`
  * `award_to(winners)`.

### **1.6 Table**

The game surface where all components interact.

* **Attributes:**

  * `table_id`
  * `seats[]` (players)
  * `dealer_button`
  * `small_blind`, `big_blind`
  * `community_cards[]`
  * `pot`
  * `deck`
* **Methods:**

  * `add_player(player)`
  * `remove_player(player)`
  * `get_next_active_player(current_pos)`
  * `reset_hand()`.

### **1.7 Action**

Simple structure to represent one player decision.

* **Attributes:** `player`, `type`, `amount`.
* **Type Enum:** `FOLD`, `CHECK`, `CALL`, `BET`, `RAISE`, `ALL_IN`.

### **1.8 GameState**

The controller object managing temporal flow.

* **Attributes:**

  * `phase` (Enum: `PRE_FLOP`, `FLOP`, `TURN`, `RIVER`, `SHOWDOWN`)
  * `current_bet`
  * `pot_ref`
  * `active_players`
  * `to_act_index`
  * `table_ref`
* **Methods:**

  * `advance_phase()`
  * `next_to_act()`
  * `execute_action(action)`
  * `resolve_bets()`
  * `showdown()`.

---

## 2. Sequence of Game State Traversal

### **2.1 Table Setup**

```text
create Table(small_blind=1, big_blind=2)
dealer = Dealer(table)
for i in players: table.add_player(i)
```

→ Each `Player` gets assigned a `seat_position`.

### **2.2 Hand Initialization**

1. `table.reset_hand()`
2. `dealer.shuffle_deck()`
3. `dealer.rotate_button()`
4. `dealer.collect_blinds()` → deducts chips, adds to pot.
5. `dealer.deal_hole_cards()` → two cards per active player.
6. Create `game_state = GameState(table)` with phase `PRE_FLOP`.

---

## 3. Round of Actions (Betting Loop)

Each betting phase runs through this finite-state loop:

```
while not game_state.round_complete():
    player = game_state.next_to_act()
    action = player.decide_action(game_state)
    game_state.execute_action(action)
game_state.resolve_bets()
```

**Order of Play:**

* **Pre-flop:** Starts left of big blind.
* **Post-flop:** Starts left of dealer.
  `game_state.next_to_act()` auto-skips folded/all-in players.

**Action Processing (`execute_action`)**

1. Validate legality (min raise, sufficient chips, etc).
2. Update `player.current_bet`, `player.stack`.
3. Update `game_state.current_bet`.
4. Add chips to `pot.add_contribution()`.
5. Log action for training/self-play.

---

## 4. Phase Progression

### **4.1 Pre-Flop → Flop**

* `game_state.advance_phase()`

  * burn 1 card
  * `dealer.deal_community("FLOP")` → 3 cards
  * reset player bets to zero
  * set current bet to 0

Repeat betting loop.

### **4.2 Flop → Turn**

* Burn 1, deal 1.
* New betting round.

### **4.3 Turn → River**

* Burn 1, deal 1.
* New betting round.

### **4.4 River → Showdown**

* If ≥2 players remain:

  * `game_state.showdown()`
  * Evaluate hands (hand ranking logic)
  * `pot.award_to(winners)`
  * Distribute chips.

---

## 5. Inter-Object Flow Example

| Step | Responsible Object | Method                   | Output / Transition |
| ---- | ------------------ | ------------------------ | ------------------- |
| 1    | `Dealer`           | `collect_blinds()`       | Pot initialized     |
| 2    | `Dealer`           | `deal_hole_cards()`      | Player hands        |
| 3    | `GameState`        | `run_betting_round()`    | Pot grows           |
| 4    | `Dealer`           | `deal_community("FLOP")` | Table state updates |
| 5    | `GameState`        | `advance_phase()`        | Betting resets      |
| 6    | `GameState`        | `showdown()`             | Payouts resolved    |

---

## 6. Design Patterns Used

* **State Pattern:** `GameState.phase` controls current round logic.
* **Command Pattern:** Each `Action` encapsulates a reversible command.
* **Observer Pattern (optional):** For UI, logging, or RL agents to monitor game transitions.
* **Strategy Pattern:** Swap human/AI decision logic via `Player.decide_action()`.

---

## 7. Typical Hand Lifecycle (Summary)

```
Table.add_player() x6
↓
Dealer.rotate_button()
↓
Dealer.collect_blinds()
↓
Dealer.deal_hole_cards()
↓
GameState.run_betting_round(preflop)
↓
Dealer.deal_community(flop)
GameState.run_betting_round(flop)
↓
Dealer.deal_community(turn)
GameState.run_betting_round(turn)
↓
Dealer.deal_community(river)
GameState.run_betting_round(river)
↓
GameState.showdown()
↓
Pot.award_to(winners)
↓
Table.reset_hand()
```

---

## 8. Scaling Later

Later modules slot in seamlessly:

* **Economy Layer:** Manages player bankrolls, tables, blinds, and stake scaling.
* **AI Layer:** Self-play agents implementing GTO or exploitative logic via `decide_action()`.
* **Persistence:** DuckDB or Parquet logs for every `Action` and `GameState` transition.
* **Simulation Controller:** Runs millions of hands asynchronously.

---
