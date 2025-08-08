# A simple CLI Blackjack game.
import random

class Deck:
    """
    Represents a deck of playing cards.
    """
    def __init__(self):
        """
        Initializes a new deck of 52 cards.
        """
        self.cards = []
        self.build()

    def build(self):
        """
        Builds a standard 52-card deck.
        """
        self.cards = []
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        for suit in suits:
            for rank in ranks:
                # Using a tuple (rank, suit) for the card
                self.cards.append((rank, suit))

    def shuffle(self):
        """
        Shuffles the deck.
        """
        random.shuffle(self.cards)

    def deal(self):
        """
        Deals one card from the top of the deck.

        Raises
        ------
        IndexError
            If the deck is empty.
        """
        if not self.cards:
            raise IndexError("All cards have been dealt")
        return self.cards.pop()

class Hand:
    """
    Represents a hand of playing cards held by a player or dealer.
    """
    def __init__(self):
        """
        Initializes a hand.
        """
        self.cards = []
        self.value = 0

    def add_card(self, card):
        """
        Adds a card to the hand and recalculates its value.
        """
        self.cards.append(card)
        self.value = self.calculate_value()

    def calculate_value(self):
        """
        Calculates the value of the hand, properly handling Aces.
        """
        value = 0
        aces = 0
        for card in self.cards:
            rank = card[0]
            if rank.isdigit():
                value += int(rank)
            elif rank in ('J', 'Q', 'K'):
                value += 10
            elif rank == 'A':
                aces += 1
                value += 11

        # Adjust for aces if the total value is over 21
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    def __str__(self):
        """
        Returns a string representation of the hand.
        """
        return ", ".join([f"{rank} of {suit}" for rank, suit in self.cards])

def play_game():
    """
    Main function to play a game of Blackjack.
    """
    deck = Deck()
    deck.shuffle()

    player_hand = Hand()
    dealer_hand = Hand()

    # Deal initial cards
    for _ in range(2):
        player_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())

    # Player's turn
    while True:
        print("\n--- Your Turn ---")
        print(f"Your hand: {player_hand} (Value: {player_hand.value})")
        # Show one of the dealer's cards
        print(f"Dealer's visible card: {dealer_hand.cards[0][0]} of {dealer_hand.cards[0][1]}")

        # Check for player bust
        if player_hand.value > 21:
            print("You busted!")
            # The game would end here, but for now, we just exit the loop
            break

        # Check for player blackjack
        if player_hand.value == 21:
            print("Blackjack!")
            break

        choice = input("Do you want to (h)it or (s)tand? ").lower()

        if choice == 'h':
            player_hand.add_card(deck.deal())
        elif choice == 's':
            break
        else:
            print("Invalid input. Please enter 'h' or 's'.")

    # Dealer's turn (only if player hasn't busted)
    if player_hand.value <= 21:
        print("\n--- Dealer's Turn ---")
        print(f"Dealer's full hand: {dealer_hand} (Value: {dealer_hand.value})")

        while dealer_hand.value < 17:
            dealer_hand.add_card(deck.deal())
            print(f"Dealer hits. New hand: {dealer_hand} (Value: {dealer_hand.value})")
            if dealer_hand.value > 21:
                break # Dealer busts

        print(f"Dealer stands with a value of {dealer_hand.value}.")

    # Determine and announce the winner
    determine_winner(player_hand, dealer_hand)


def determine_winner(player_hand, dealer_hand):
    """
    Determines the winner and prints the final result.
    """
    player_value = player_hand.value
    dealer_value = dealer_hand.value

    print("\n--- Game Over ---")
    print(f"Your final hand: {player_hand} (Value: {player_value})")
    print(f"Dealer's final hand: {dealer_hand} (Value: {dealer_value})")

    if player_value > 21:
        # This case is handled in the player loop, but we keep it for clarity
        print("You busted! Dealer wins.")
    elif dealer_value > 21:
        print("Dealer busted! You win!")
    elif player_value > dealer_value:
        print("Congratulations, you win!")
    elif dealer_value > player_value:
        print("Dealer wins!")
    else:
        print("It's a push (a tie)!")


if __name__ == "__main__":
    play_game()
