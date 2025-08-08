import unittest
from blackjack import Deck, Hand, Bankroll
from blackjack import basic_strategy_hint

class TestDeck(unittest.TestCase):
    """
    Test suite for the Deck class.
    """
    def test_deck_creation(self):
        """
        Tests that a new deck has 52 cards.
        """
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        # Check for uniqueness
        self.assertEqual(len(set(deck.cards)), 52)

    def test_deck_shuffle(self):
        """
        Tests that shuffling a deck changes the card order.
        """
        deck1 = Deck()
        deck2 = Deck()
        # It's extremely improbable for a shuffled deck to be identical to a new one.
        # This test is sufficient for this project's scope.
        deck2.shuffle()
        self.assertNotEqual(deck1.cards, deck2.cards)

    def test_deck_deal(self):
        """
        Tests that dealing a card removes it from the deck.
        """
        deck = Deck()
        top_card = deck.cards[-1] # pop() removes from the end
        card = deck.deal()
        self.assertEqual(len(deck.cards), 51)
        self.assertEqual(card, top_card)
        self.assertNotIn(card, deck.cards)

    def test_deck_deal_empty(self):
        """
        Tests that dealing from an empty deck raises an error.
        """
        deck = Deck()
        for _ in range(52):
            deck.deal()
        with self.assertRaises(IndexError):
            deck.deal()

class TestHand(unittest.TestCase):
    """
    Test suite for the Hand class.
    """
    def test_hand_value_simple(self):
        """
        Tests hand value with no aces.
        """
        hand = Hand()
        hand.add_card(('5', 'Hearts'))
        hand.add_card(('K', 'Spades'))
        self.assertEqual(hand.value, 15)

    def test_hand_value_with_aces(self):
        """
        Tests hand value with one or more aces.
        """
        # Ace as 11
        hand = Hand()
        hand.add_card(('A', 'Clubs'))
        hand.add_card(('9', 'Diamonds'))
        self.assertEqual(hand.value, 20)

        # Ace as 1
        hand.add_card(('5', 'Hearts'))
        self.assertEqual(hand.value, 15) # A(1) + 9 + 5

        # Blackjack
        hand = Hand()
        hand.add_card(('A', 'Spades'))
        hand.add_card(('J', 'Clubs'))
        self.assertEqual(hand.value, 21)

        # Multiple Aces
        hand = Hand()
        hand.add_card(('A', 'Hearts'))
        hand.add_card(('A', 'Diamonds'))
        self.assertEqual(hand.value, 12) # 11 + 1

        hand.add_card(('A', 'Clubs'))
        self.assertEqual(hand.value, 13) # 11 + 1 + 1

        hand.add_card(('8', 'Spades'))
        self.assertEqual(hand.value, 21) # 11 + 1 + 1 + 8


class TestBankroll(unittest.TestCase):
    """Test suite for the Bankroll class."""

    def test_bet_and_win(self):
        bank = Bankroll(100)
        bank.bet(10)
        self.assertEqual(bank.amount, 90)
        bank.win(10)
        self.assertEqual(bank.amount, 110)

    def test_push(self):
        bank = Bankroll(50)
        bank.bet(20)
        bank.push(20)
        self.assertEqual(bank.amount, 50)

    def test_invalid_bet(self):
        bank = Bankroll(5)
        with self.assertRaises(ValueError):
            bank.bet(10)


class TestStrategy(unittest.TestCase):
    def test_pair_split_hint(self):
        hand = Hand()
        hand.add_card(("8", "Hearts"))
        hand.add_card(("8", "Diamonds"))
        hint = basic_strategy_hint(hand, "5")
        self.assertEqual(hint, "Split")

    def test_soft_hint(self):
        hand = Hand()
        hand.add_card(("A", "Hearts"))
        hand.add_card(("7", "Clubs"))
        hint = basic_strategy_hint(hand, "9")
        self.assertEqual(hint, "Hit")

    def test_hard_hint(self):
        hand = Hand()
        hand.add_card(("5", "Hearts"))
        hand.add_card(("6", "Clubs"))
        hint = basic_strategy_hint(hand, "6")
        self.assertEqual(hint, "Double")

if __name__ == '__main__':
    unittest.main()
