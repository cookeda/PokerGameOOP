<!-- 6775429b-080d-4ff1-b88c-0211f1f2ad2f bff30116-ffe6-458c-bebc-0a6b91b250aa -->
# Comprehensive Test Plan for Poker Game OOP

## Test Structure

Tests will be organized into unit tests (individual components) and integration tests (component interactions). All tests will use controlled environments with specific initial states. Must use pytest

## 1. Action System Tests (`test_action.py`)

### 1.1 ActionType Enum Tests

- Test all enum values exist (FOLD, CHECK, CALL, BET, RAISE, ALL_IN)
- Test enum value strings are correct

### 1.2 Action Class Tests

- **Test Action Creation**: Create actions for each type with valid parameters
- **Test Action String Representation**: Verify `__str__()` returns correct format for each action type
- **Test Action Repr**: Verify `__repr__()` returns correct format
- **Test Action with Zero Amount**: Verify actions that don't need amounts work correctly
- **Test Action with Amount**: Verify bet/raise/call actions store amounts correctly

## 2. Pot Management Tests (`test_pot.py`)

### 2.1 Basic Pot Operations

- **Test Initialization**: Pot starts with zero main_pot, empty side_pots, empty contributors
- **Test Add Contribution**: Add chips from single player, verify main_pot and contributors update
- **Test Multiple Contributions**: Add chips from multiple players, verify totals
- **Test Get Total**: Verify get_total() returns correct sum including side pots

### 2.2 Side Pot Resolution

- **Test Single All-In**: One player all-in, verify no side pots created
- **Test Two All-Ins Different Amounts**: 
- Player A: 100 chips all-in
- Player B: 50 chips all-in
- Verify side pot created with correct amounts and contributors
- **Test Three All-Ins**: Multiple all-in amounts, verify multiple side pots created correctly
- **Test Side Pot Calculation**: Verify main pot reduced correctly when side pots created

### 2.3 Pot Awarding

- **Test Award to Single Winner**: Award main pot to one winner, verify stack increases correctly
- **Test Award to Multiple Winners**: Split pot between winners, verify remainder distributed
- **Test Award with Side Pots**: Award main pot and side pots to different winners
- **Test Award with Remainder**: Pot not divisible by winners, verify remainder distributed one chip at a time

### 2.4 Pot Reset

- **Test Reset**: Reset pot after awarding, verify all values return to initial state

## 3. Player Tests (`test_player.py`)

### 3.1 Player Initialization

- **Test Basic Creation**: Create player with name and stack, verify attributes initialized
- **Test Human vs AI Flag**: Verify is_human flag set correctly
- **Test Initial State**: Verify current_bet=0, is_active=True, has_folded=False, is_all_in=False

### 3.2 Player Action Methods

- **Test Post Blind**: Post small/big blind, verify stack decreases, current_bet increases
- **Test Post Blind Insufficient Chips**: Post blind when stack < amount, verify only posts available chips
- **Test Bet**: Place bet, verify stack and current_bet update correctly
- **Test Bet All-In**: Bet entire stack, verify is_all_in flag set
- **Test Call**: Call amount, verify stack decreases, current_bet increases
- **Test Call Partial**: Call when stack < call amount, verify only calls available chips
- **Test Fold**: Fold hand, verify has_folded=True, is_active=False
- **Test Check**: Check action, verify no state changes
- **Test All-In**: Go all-in, verify stack=0, is_all_in=True, current_bet updated

### 3.3 Player State Management

- **Test Reset Hand State**: Reset player after hand, verify all state attributes reset correctly
- **Test Seat Position Assignment**: Verify seat_position set when added to table

### 3.4 Player Decision Interface

- **Test Decide Action Human**: Mock human input, verify correct Action returned
- **Test Decide Action AI**: Create AI player subclass, verify get_action() called
- **Test Invalid Input Handling**: Test error handling for invalid human inputs

## 4. Table Tests (`test_table.py`)

### 4.1 Table Initialization

- **Test Default Creation**: Create table with default 6 seats
- **Test Custom Seats**: Create table with custom number of seats
- **Test Blinds**: Verify small_blind and big_blind set correctly
- **Test Initial State**: Verify pot, dealer_button, community_cards initialized

### 4.2 Player Management

- **Test Add Player**: Add player to table, verify assigned to seat
- **Test Add Player Specific Seat**: Add player to specific seat index
- **Test Add Player Auto Seat**: Add player without specifying seat, verify assigned to first available
- **Test Add Player Full Table**: Attempt to add player when table full, verify error
- **Test Remove Player**: Remove player from table, verify seat cleared
- **Test Remove Player Not Found**: Attempt to remove non-existent player, verify error

### 4.3 Active Player Management

- **Test Get Active Players**: Get list of active players, verify only active players returned
- **Test Get Next Active Player**: Find next active player from current position
- **Test Get Next Active Player Wraps**: Verify wraps around table correctly
- **Test Get Next Active Player None**: No active players, verify returns None

### 4.4 Table Reset

- **Test Reset Hand**: Reset table for new hand, verify community cards cleared, pot reset, players reset

## 5. Dealer Tests (`test_dealer.py`)

### 5.1 Dealer Initialization

- **Test Dealer Creation**: Create dealer with table and deck
- **Test Deck Shuffled**: Verify deck shuffled on initialization

### 5.2 Card Dealing

- **Test Deal Card**: Deal single card to player, verify card added to hand
- **Test Deal Hole Cards**: Deal hole cards to all active players, verify 2 cards each
- **Test Deal Hole Cards Inactive**: Verify inactive players don't receive cards
- **Test Deal Community Cards**: Deal n community cards, verify cards added to table
- **Test Deal Community with Burn**: Verify burn card dealt before community cards
- **Test Deal Community Flop**: Deal flop, verify 3 cards + 1 burn
- **Test Deal Community Turn**: Deal turn, verify 1 card + 1 burn
- **Test Deal Community River**: Deal river, verify 1 card + 1 burn
- **Test Deal Community Invalid Stage**: Invalid stage, verify error

### 5.3 Button Management

- **Test Rotate Button**: Rotate button to next active player
- **Test Rotate Button Wraps**: Verify wraps around table
- **Test Rotate Button No Players**: No active players, verify button still rotates

### 5.4 Blind Collection

- **Test Collect Blinds**: Collect small and big blinds, verify chips deducted
- **Test Collect Blinds Positions**: Verify correct players post blinds (SB=button+1, BB=button+2)
- **Test Collect Blinds Insufficient Chips**: Player has less than blind, verify only posts available
- **Test Collect Blinds Updates Pot**: Verify blinds added to pot

## 6. GameState Tests (`test_gamestate.py`)

### 6.1 GameState Initialization

- **Test GameState Creation**: Create GameState with table and pot
- **Test Initial Phase**: Verify phase is PRE_FLOP
- **Test Initial Bet**: Verify current_bet = 0
- **Test Active Players**: Verify active_players list populated correctly
- **Test Starting Position Pre-Flop**: Verify to_act_index set to left of big blind
- **Test Starting Position Post-Flop**: Create GameState in post-flop phase, verify to_act_index set correctly

### 6.2 Turn Management

- **Test Next To Act**: Get next player to act, verify correct player returned
- **Test Next To Act Skips Folded**: Verify folded players skipped
- **Test Next To Act Skips All-In**: Verify all-in players skipped
- **Test Next To Act Round Complete**: Round complete, verify returns None
- **Test Next To Act Wraps**: Verify wraps around table correctly

### 6.3 Valid Actions

- **Test Get Valid Actions No Bet**: No current bet, verify CHECK and BET available
- **Test Get Valid Actions With Bet**: Current bet exists, verify CALL and RAISE available
- **Test Get Valid Actions Insufficient Chips**: Player can't afford call, verify only FOLD and ALL_IN
- **Test Get Call Amount**: Calculate call amount correctly
- **Test Get Call Amount Zero**: No bet to call, verify returns 0

### 6.4 Action Execution

- **Test Execute Fold**: Execute fold action, verify player folded, removed from active
- **Test Execute Check**: Execute check with no bet, verify no errors
- **Test Execute Check With Bet**: Attempt check when bet exists, verify error
- **Test Execute Call**: Execute call, verify chips deducted, pot updated, current_bet matched
- **Test Execute Bet**: Execute bet, verify chips deducted, pot updated, current_bet set
- **Test Execute Bet Invalid**: Bet when bet exists, verify error
- **Test Execute Bet Below Minimum**: Bet below min_raise, verify error
- **Test Execute Raise**: Execute raise, verify chips deducted, current_bet updated, last_raiser set
- **Test Execute Raise Below Minimum**: Raise below minimum, verify error
- **Test Execute All-In**: Execute all-in, verify player all-in, pot updated
- **Test Execute Action Inactive Player**: Attempt action from inactive player, verify error
- **Test Execute Invalid Action**: Invalid action type for situation, verify error

### 6.5 Round Completion

- **Test Round Complete All Matched**: All players matched bet, verify round complete
- **Test Round Complete With Raise**: Raise occurred, verify round complete when action returns to raiser
- **Test Round Complete One Player**: Only one player remains, verify round complete
- **Test Round Complete Not Complete**: Players haven't matched, verify round not complete

### 6.6 Bet Resolution

- **Test Resolve Bets**: Resolve bets at end of round, verify current_bet reset, player bets reset
- **Test Resolve Bets History**: Verify action_history cleared

### 6.7 Phase Advancement

- **Test Advance Phase Pre-Flop to Flop**: Advance to flop, verify phase changed, flop dealt, bets resolved
- **Test Advance Phase Flop to Turn**: Advance to turn, verify phase changed, turn dealt
- **Test Advance Phase Turn to River**: Advance to river, verify phase changed, river dealt
- **Test Advance Phase River to Showdown**: Advance to showdown, verify phase changed
- **Test Advance Phase Invalid**: Attempt advance from showdown, verify error

### 6.8 Showdown

- **Test Showdown**: Execute showdown, verify phase set to SHOWDOWN

## 7. Integration Tests (`test_integration.py`)

### 7.1 Complete Hand Scenarios

- **Test Complete Hand All Fold**: All players fold except one, verify pot awarded correctly
- **Test Complete Hand Check Down**: All players check to showdown, verify all phases completed
- **Test Complete Hand With Betting**: Hand with betting on each street, verify pot grows correctly
- **Test Complete Hand All-In**: Multiple all-ins, verify side pots created and awarded correctly

### 7.2 Betting Round Scenarios

- **Test Pre-Flop Betting Round**: Complete pre-flop betting round with various actions
- **Test Post-Flop Betting Round**: Complete post-flop betting round
- **Test Betting Round With Raise**: Betting round with raises, verify round completes correctly
- **Test Betting Round All Fold**: All players fold during betting round

### 7.3 Edge Cases

- **Test Player Goes All-In Less Than Bet**: Player all-in for less than current bet, verify handled correctly
- **Test Multiple Raises**: Multiple raises in same round, verify last_raiser tracked correctly
- **Test Button Rotation**: Multiple hands, verify button rotates correctly
- **Test Insufficient Chips Scenarios**: Various scenarios with players having insufficient chips

## 8. Controlled Environment Test Scenarios

### 8.1 Scenario: Two Player Heads-Up

- Setup: 2 players, 100 chips each, blinds 1/2
- Actions: Complete hand with controlled actions
- Verify: Pot calculations, state transitions, winner determination

### 8.2 Scenario: Three Player with All-In

- Setup: 3 players with different stack sizes (100, 50, 75)
- Actions: Player with 50 goes all-in, others call
- Verify: Side pot created correctly, main pot and side pot awarded correctly

### 8.3 Scenario: Full Table Pre-Flop Fold

- Setup: 6 players, all active
- Actions: First player bets, all others fold
- Verify: Round completes immediately, pot awarded to bettor

### 8.4 Scenario: Check Down to Showdown

- Setup: 2 players, no betting
- Actions: All players check through all streets
- Verify: All phases advance correctly, showdown reached

### 8.5 Scenario: Raise War

- Setup: 2 players, sufficient chips
- Actions: Multiple raises back and forth
- Verify: Round completes when action returns to last raiser

## 9. Error Handling Tests

### 9.1 Invalid Input Tests

- **Test Invalid Action Amounts**: Negative amounts, amounts exceeding stack
- **Test Invalid Action Types**: Invalid action types for current game state
- **Test Invalid Player States**: Actions from folded/inactive players
- **Test Invalid Phase Transitions**: Invalid phase advancement attempts

### 9.2 Boundary Condition Tests

- **Test Zero Stack Player**: Player with zero stack, verify handled correctly
- **Test Maximum Stack**: Very large stack values, verify no overflow
- **Test Empty Table**: Operations on empty table
- **Test Single Player**: Table with only one player

## 10. Test Utilities and Fixtures

### 10.1 Test Fixtures

- **create_test_table()**: Helper to create table with specified players
- **create_test_game_state()**: Helper to create GameState in specific phase
- **create_test_players()**: Helper to create players with specified stacks
- **mock_deck()**: Helper to create deck with known card order for deterministic tests

### 10.2 Mock Objects

- **MockPlayer**: AI player that returns predetermined actions
- **MockDeck**: Deck with controlled card order
- **MockGameState**: GameState with specific controlled state

## Test Implementation Notes

1. **Use pytest** as the testing framework
2. **Use fixtures** for common test setup
3. **Use parametrize** for testing multiple similar scenarios
4. **Use mocks** for human input and random elements
5. **Use controlled seeds** for deck shuffling to ensure reproducibility
6. **Verify state changes** explicitly (before/after comparisons)
7. **Test both success and failure paths**
8. **Use descriptive test names** that explain what is being tested
9. **Group related tests** in classes or modules
10. **Test edge cases** thoroughly (zero values, maximum values, boundary conditions)

### To-dos

- [x] Create Action.py with ActionType enum and Action class
- [x] Create Pot.py with pot tracking and side pot logic
- [x] Enhance Player.py with state attributes (current_bet, is_active, etc.) and action methods (bet, call, fold, check)
- [x] Enhance Table.py with pot, blinds, dealer_button, and game state support
- [x] Enhance Dealer.py with rotate_button(), collect_blinds(), and deal_community() methods
- [x] Create GameState.py with Phase enum, betting loop logic, action execution, and validation
- [x] Implement human console input interface in Player.decide_action() with game state display and input parsing
- [x] Add comprehensive action validation in GameState.execute_action() (min raise, sufficient chips, legal actions)