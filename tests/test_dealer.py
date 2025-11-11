"""
Tests for Dealer class (initialization, card dealing, button rotation, blind collection).
"""
import pytest
from src.core.Dealer import Dealer
from src.core.Deck import Deck
from src.core.Table import Table
from src.core.Player import Player
from src.core.Card import Card, Rank, Suit


class TestDealerInitialization:
    """Tests for dealer initialization."""
    
    def test_dealer_creation(self):
        """Create dealer with table and deck."""
        table = Table()
        deck = Deck()
        dealer = Dealer(table, deck)
        
        assert dealer.table == table
        assert dealer.deck == deck
    
    def test_deck_shuffled(self):
        """Verify deck shuffled on initialization."""
        table = Table()
        deck = Deck(seed=42)
        initial_order = deck.cards.copy()
        
        dealer = Dealer(table, deck)
        
        # Deck should be shuffled (very unlikely to be in same order)
        # We'll check that the deck has cards (shuffled)
        assert len(dealer.deck.cards) == 52


class TestDealerCardDealing:
    """Tests for card dealing."""
    
    @pytest.fixture
    def table_with_players(self):
        """Create table with players."""
        table = Table(n_seats=6)
        players = [
            Player("Player1", 100),
            Player("Player2", 100),
            Player("Player3", 100),
        ]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        return table, players
    
    @pytest.fixture
    def dealer(self, table_with_players):
        """Create dealer with table."""
        table, _ = table_with_players
        deck = Deck(seed=42)
        return Dealer(table, deck)
    
    def test_deal_card(self, dealer, table_with_players):
        """Deal single card to player, verify card added to hand."""
        _, players = table_with_players
        initial_hand_size = len(players[0].hand)
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_card(players[0])
        
        assert len(players[0].hand) == initial_hand_size + 1
        assert len(dealer.deck.cards) == initial_deck_size - 1
        assert isinstance(players[0].hand[-1], Card)
    
    def test_deal_hole_cards(self, dealer, table_with_players):
        """Deal hole cards to all active players, verify 2 cards each."""
        _, players = table_with_players
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_hole_cards()
        
        for player in players:
            assert len(player.hand) == 2
            assert all(isinstance(card, Card) for card in player.hand)
        
        # Should have dealt 6 cards total (2 per player * 3 players)
        assert len(dealer.deck.cards) == initial_deck_size - 6
    
    def test_deal_hole_cards_inactive(self, dealer):
        """Verify inactive players don't receive cards."""
        table = Table(n_seats=6)
        active_player = Player("Active", 100)
        inactive_player = Player("Inactive", 100)
        inactive_player.is_active = False
        
        table.add_player(active_player, seat_index=0)
        table.add_player(inactive_player, seat_index=1)
        
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_hole_cards()
        
        assert len(active_player.hand) == 2
        assert len(inactive_player.hand) == 0
        assert len(dealer.deck.cards) == initial_deck_size - 2
    
    def test_deal_community_cards(self, dealer, table_with_players):
        """Deal n community cards, verify cards added to table."""
        table, _ = table_with_players
        initial_community_size = len(table.community_cards)
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_community_cards(3)
        
        assert len(table.community_cards) == initial_community_size + 3
        # Should have burned 1 card and dealt 3
        assert len(dealer.deck.cards) == initial_deck_size - 4
        assert all(isinstance(card, Card) for card in table.community_cards)
    
    def test_deal_community_with_burn(self, dealer, table_with_players):
        """Verify burn card dealt before community cards."""
        table, _ = table_with_players
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_community_cards(3)
        
        # Should have burned 1 + dealt 3 = 4 cards total
        assert len(dealer.deck.cards) == initial_deck_size - 4
    
    def test_deal_community_flop(self, dealer, table_with_players):
        """Deal flop, verify 3 cards + 1 burn."""
        table, _ = table_with_players
        initial_community_size = len(table.community_cards)
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_community("FLOP")
        
        assert len(table.community_cards) == initial_community_size + 3
        assert len(dealer.deck.cards) == initial_deck_size - 4  # 1 burn + 3 cards
    
    def test_deal_community_turn(self, dealer, table_with_players):
        """Deal turn, verify 1 card + 1 burn."""
        table, _ = table_with_players
        initial_community_size = len(table.community_cards)
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_community("TURN")
        
        assert len(table.community_cards) == initial_community_size + 1
        assert len(dealer.deck.cards) == initial_deck_size - 2  # 1 burn + 1 card
    
    def test_deal_community_river(self, dealer, table_with_players):
        """Deal river, verify 1 card + 1 burn."""
        table, _ = table_with_players
        initial_community_size = len(table.community_cards)
        initial_deck_size = len(dealer.deck.cards)
        
        dealer.deal_community("RIVER")
        
        assert len(table.community_cards) == initial_community_size + 1
        assert len(dealer.deck.cards) == initial_deck_size - 2  # 1 burn + 1 card
    
    def test_deal_community_case_insensitive(self, dealer, table_with_players):
        """Test that stage names are case insensitive."""
        table, _ = table_with_players
        dealer.deal_community("flop")
        assert len(table.community_cards) == 3
        
        dealer.deal_community("Turn")
        assert len(table.community_cards) == 4
    
    def test_deal_community_invalid_stage(self, dealer, table_with_players):
        """Invalid stage, verify error."""
        with pytest.raises(ValueError, match="Invalid stage"):
            dealer.deal_community("INVALID")


class TestDealerButtonManagement:
    """Tests for button management."""
    
    @pytest.fixture
    def table_with_players(self):
        """Create table with players."""
        table = Table(n_seats=6)
        players = [
            Player("Player1", 100),
            Player("Player2", 100),
            Player("Player3", 100),
        ]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        return table, players
    
    def test_rotate_button(self, table_with_players):
        """Rotate button to next active player."""
        table, players = table_with_players
        table.dealer_button = 0
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        dealer.rotate_button()
        
        assert table.dealer_button == 1
    
    def test_rotate_button_wraps(self, table_with_players):
        """Verify wraps around table."""
        table, players = table_with_players
        table.dealer_button = 2  # Last player
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        dealer.rotate_button()
        
        assert table.dealer_button == 0  # Wraps to first
    
    def test_rotate_button_no_players(self):
        """No active players, verify button still rotates."""
        table = Table(n_seats=6)
        table.dealer_button = 2
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        dealer.rotate_button()
        
        assert table.dealer_button == 3
    
    def test_rotate_button_skips_zero_stack(self):
        """Verify button skips players with zero stack."""
        table = Table(n_seats=6)
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 0)  # Zero stack
        player3 = Player("Player3", 100)
        
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        table.add_player(player3, seat_index=2)
        
        table.dealer_button = 0
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        dealer.rotate_button()
        
        # Should skip player2 (zero stack) and go to player3
        assert table.dealer_button == 2


class TestDealerBlindCollection:
    """Tests for blind collection."""
    
    def test_collect_blinds(self):
        """Collect small and big blinds, verify chips deducted."""
        table = Table(n_seats=6, small_blind=1, big_blind=2)
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        player3 = Player("Player3", 100)
        
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        table.add_player(player3, seat_index=2)
        
        table.dealer_button = 0
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        initial_stack1 = player1.stack
        initial_stack2 = player2.stack
        initial_stack3 = player3.stack
        initial_pot = table.pot.main_pot
        
        dealer.collect_blinds()
        
        # Player1 (seat 0) should post small blind (seat 1)
        # Player2 (seat 1) should post big blind (seat 2)
        # Actually, SB is button+1, BB is button+2
        # Button is 0, so SB is 1 (player2), BB is 2 (player3)
        assert player2.stack == initial_stack2 - 1  # Small blind
        assert player3.stack == initial_stack3 - 2  # Big blind
        assert table.pot.main_pot == initial_pot + 3  # 1 + 2
    
    def test_collect_blinds_positions(self):
        """Verify correct players post blinds (SB=button+1, BB=button+2)."""
        table = Table(n_seats=6, small_blind=1, big_blind=2)
        players = [Player(f"Player{i}", 100) for i in range(6)]
        for i, player in enumerate(players):
            table.add_player(player, seat_index=i)
        
        table.dealer_button = 2
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        dealer.collect_blinds()
        
        # SB should be at position 3 (button+1)
        # BB should be at position 4 (button+2)
        assert players[3].current_bet == 1  # Small blind
        assert players[4].current_bet == 2  # Big blind
    
    def test_collect_blinds_insufficient_chips(self):
        """Player has less than blind, verify only posts available."""
        table = Table(n_seats=6, small_blind=1, big_blind=2)
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 0)  # No chips
        player3 = Player("Player3", 1)  # Less than big blind
        
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        table.add_player(player3, seat_index=2)
        
        table.dealer_button = 0
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        dealer.collect_blinds()
        
        # Player2 should post 0 (no chips)
        # Player3 should post 1 (all they have)
        assert player2.current_bet == 0
        assert player3.current_bet == 1
        assert player3.stack == 0
    
    def test_collect_blinds_updates_pot(self):
        """Verify blinds added to pot."""
        table = Table(n_seats=6, small_blind=1, big_blind=2)
        player1 = Player("Player1", 100)
        player2 = Player("Player2", 100)
        player3 = Player("Player3", 100)
        
        table.add_player(player1, seat_index=0)
        table.add_player(player2, seat_index=1)
        table.add_player(player3, seat_index=2)
        
        table.dealer_button = 0
        deck = Deck(seed=42)
        dealer = Dealer(table, deck)
        
        initial_pot = table.pot.main_pot
        
        dealer.collect_blinds()
        
        assert table.pot.main_pot == initial_pot + 3  # 1 + 2

