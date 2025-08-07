import unittest
from blackjack import Deck, Hand

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

if __name__ == '__main__':
    unittest.main()
