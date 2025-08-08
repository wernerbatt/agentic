# A simple CLI Blackjack game.
import random
import sys

try:
    import termios
    import tty

    def getch():
        """Read a single character from stdin without requiring Enter."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
except (ImportError, AttributeError):  # pragma: no cover - Windows fallback
    import msvcrt

    def getch():
        return msvcrt.getch().decode("utf-8")


class Bankroll:
    """Represents a player's bankroll."""

    def __init__(self, amount: int = 100):
        self.amount = amount

    def bet(self, amount: int) -> int:
        """Place a bet and deduct it from the bankroll."""
        if amount <= 0 or amount > self.amount:
            raise ValueError("Invalid bet amount")
        self.amount -= amount
        return amount

    def win(self, bet: int) -> None:
        """Add winnings for a successful bet."""
        self.amount += bet * 2

    def push(self, bet: int) -> None:
        """Return the bet to the bankroll on a push."""
        self.amount += bet

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

    def is_pair(self):
        """Return True if the hand is a pair."""
        return len(self.cards) == 2 and self.cards[0][0] == self.cards[1][0]

    def is_soft(self):
        """Return True if the hand is a soft hand (contains an ace counted as 11)."""
        total = 0
        aces = 0
        for rank, _ in self.cards:
            if rank == "A":
                aces += 1
            elif rank in ("J", "Q", "K") or rank == "10":
                total += 10
            else:
                total += int(rank)
        total += aces  # count all aces as 1
        return aces > 0 and total + 10 <= 21

    def __str__(self):
        """
        Returns a string representation of the hand.
        """
        return ", ".join([f"{rank} of {suit}" for rank, suit in self.cards])


def _card_value(rank: str) -> int:
    """Return the blackjack value of a card rank."""
    if rank in ("J", "Q", "K", "10"):
        return 10
    if rank == "A":
        return 11
    return int(rank)


def _normalize_rank(rank: str) -> str:
    """Map face cards to '10' for pair comparisons."""
    return "10" if rank in ("J", "Q", "K") else rank


def basic_strategy_hint(
    hand: Hand, dealer_upcard: str, can_split: bool = True, can_double: bool = True
) -> tuple[str, str]:
    """Return the basic strategy recommendation and a short reason."""
    dealer = _card_value(dealer_upcard)

    if can_split and hand.is_pair():
        rank = _normalize_rank(hand.cards[0][0])
        if rank == "A":
            return "Split", "Always split aces."
        if rank == "10":
            return "Stand", "Never split tens; stand instead."
        if rank == "9":
            if dealer in [2, 3, 4, 5, 6, 8, 9]:
                return "Split", f"Split 9s against dealer {dealer_upcard}."
            return "Stand", f"Stand on 18 against dealer {dealer_upcard}."
        if rank == "8":
            return "Split", "Pair of 8s should always be split."
        if rank == "7":
            return (
                "Split" if 2 <= dealer <= 7 else "Hit",
                f"Pair of 7s vs dealer {dealer_upcard}.",
            )
        if rank == "6":
            return (
                "Split" if 2 <= dealer <= 6 else "Hit",
                f"Pair of 6s vs dealer {dealer_upcard}.",
            )
        if rank == "5":
            return (
                "Double" if can_double and 2 <= dealer <= 9 else "Hit",
                f"Pair of 5s vs dealer {dealer_upcard}.",
            )
        if rank == "4":
            return (
                "Split" if dealer in [5, 6] else "Hit",
                f"Pair of 4s vs dealer {dealer_upcard}.",
            )
        if rank in {"3", "2"}:
            return (
                "Split" if 2 <= dealer <= 7 else "Hit",
                f"Pair of {rank}s vs dealer {dealer_upcard}.",
            )

    if hand.is_soft():
        total = hand.value
        if total >= 19:
            if total == 19 and dealer == 6 and can_double:
                return "Double", "Soft 19 doubles against dealer 6."
            return "Stand", f"Soft {total} should stand."
        if total == 18:
            if dealer in [3, 4, 5, 6]:
                action = "Double" if can_double else "Stand"
                reason = "Double" if can_double else "Stand"
                return action, f"Soft 18 {reason.lower()}s against dealer {dealer_upcard}."
            if dealer in [2, 7, 8]:
                return "Stand", f"Soft 18 stands against dealer {dealer_upcard}."
            return "Hit", f"Soft 18 hits against dealer {dealer_upcard}."
        if total == 17:
            action = "Double" if can_double and 3 <= dealer <= 6 else "Hit"
            return action, f"Soft 17 vs dealer {dealer_upcard}."
        if total in (15, 16):
            action = "Double" if can_double and 4 <= dealer <= 6 else "Hit"
            return action, f"Soft {total} vs dealer {dealer_upcard}."
        if total in (13, 14):
            action = "Double" if can_double and dealer in [5, 6] else "Hit"
            return action, f"Soft {total} vs dealer {dealer_upcard}."

    total = hand.value
    if total >= 17:
        return "Stand", f"Hard {total} stands." 
    if 13 <= total <= 16:
        action = "Stand" if 2 <= dealer <= 6 else "Hit"
        return action, f"Hard {total} {action.lower()}s against dealer {dealer_upcard}."
    if total == 12:
        action = "Stand" if 4 <= dealer <= 6 else "Hit"
        return action, f"Hard 12 {action.lower()}s against dealer {dealer_upcard}."
    if total == 11:
        action = "Double" if can_double and 2 <= dealer <= 10 else "Hit"
        verb = "doubles" if action == "Double" else "hits"
        return action, f"Hard 11 {verb} against dealer {dealer_upcard}."
    if total == 10:
        action = "Double" if can_double and 2 <= dealer <= 9 else "Hit"
        verb = "doubles" if action == "Double" else "hits"
        return action, f"Hard 10 {verb} against dealer {dealer_upcard}."
    if total == 9:
        action = "Double" if can_double and 3 <= dealer <= 6 else "Hit"
        verb = "doubles" if action == "Double" else "hits"
        return action, f"Hard 9 {verb} against dealer {dealer_upcard}."
    return "Hit", f"Hard {total} hits against dealer {dealer_upcard}."

def play_game():
    """Main loop for a Blackjack session with a fixed bet."""
    deck = Deck()
    deck.shuffle()
    bankroll = Bankroll()
    bet = 10

    while bankroll.amount >= bet:
        print(f"\nBankroll: £{bankroll.amount}")
        bankroll.bet(bet)
        print(f"Betting £{bet}")

        player_hands = [Hand()]
        dealer_hand = Hand()
        for _ in range(2):
            player_hands[0].add_card(deck.deal())
            dealer_hand.add_card(deck.deal())
        bets = [bet]

        hand_index = 0
        while hand_index < len(player_hands):
            hand = player_hands[hand_index]
            while True:
                print("\n--- Your Turn ---")
                print(f"Hand {hand_index + 1}: {hand} (Value: {hand.value})")
                print(
                    f"Dealer's visible card: {dealer_hand.cards[0][0]} of {dealer_hand.cards[0][1]}"
                )

                if hand.value > 21:
                    print("You busted!")
                    break
                if hand.value == 21:
                    if len(hand.cards) == 2:
                        print("Blackjack!")
                    else:
                        print("21!")
                    break

                can_split = (
                    hand.is_pair()
                    and len(player_hands) == 1
                    and len(hand.cards) == 2
                    and bankroll.amount >= bets[hand_index]
                )
                can_double = (
                    len(hand.cards) == 2 and bankroll.amount >= bets[hand_index]
                )
                hint, reason = basic_strategy_hint(
                    hand, dealer_hand.cards[0][0], can_split, can_double
                )
                options = "(h)it or (s)tand"
                if can_double:
                    options += ", (d)ouble"
                if can_split:
                    options += ", s(p)lit"
                options += ", show (t)ip"
                print(f"Do you want to {options}? ", end="", flush=True)
                choice = getch()
                if choice == "\x1b":
                    bankroll.push(bets[hand_index])
                    if hand_index + 1 < len(player_hands):
                        bankroll.push(sum(bets[hand_index + 1 :]))
                    print("\nExiting game.")
                    print(f"Final bankroll: £{bankroll.amount}")
                    return
                choice = choice.lower()
                print(choice)
                if choice == "t":
                    print(f"Hint: {hint} ({reason})")
                    continue

                action_map = {"h": "Hit", "s": "Stand", "d": "Double", "p": "Split"}
                player_action = action_map.get(choice)

                if player_action and player_action != hint:
                    print(
                        f"\033[91mYou chose to {player_action}, but the optimal move was to {hint.lower()}.\033[0m"
                    )

                if choice == "h":
                    hand.add_card(deck.deal())
                elif choice == "s":
                    break
                elif choice == "d" and can_double:
                    bankroll.bet(bets[hand_index])
                    bets[hand_index] *= 2
                    hand.add_card(deck.deal())
                    break
                elif choice == "p" and can_split:
                    bankroll.bet(bets[hand_index])
                    card1 = hand.cards[0]
                    card2 = hand.cards[1]
                    new_hand1 = Hand()
                    new_hand1.add_card(card1)
                    new_hand1.add_card(deck.deal())
                    new_hand2 = Hand()
                    new_hand2.add_card(card2)
                    new_hand2.add_card(deck.deal())
                    player_hands = [new_hand1, new_hand2]
                    bets = [bets[hand_index], bets[hand_index]]
                    hand_index = 0
                    hand = player_hands[hand_index]
                    continue
                else:
                    print("Invalid input. Please try again.")
            hand_index += 1

        if any(h.value <= 21 for h in player_hands):
            print("\n--- Dealer's Turn ---")
            print(f"Dealer's full hand: {dealer_hand} (Value: {dealer_hand.value})")
            while dealer_hand.value < 17:
                dealer_hand.add_card(deck.deal())
                print(
                    f"Dealer hits. New hand: {dealer_hand} (Value: {dealer_hand.value})"
                )
                if dealer_hand.value > 21:
                    break
            print(f"Dealer stands with a value of {dealer_hand.value}.")

        for h, b in zip(player_hands, bets):
            result = determine_winner(h, dealer_hand)
            if result == "player":
                bankroll.win(b)
            elif result == "push":
                bankroll.push(b)

        if bankroll.amount < bet:
            print("You're out of money!")
            break
        # rebuild deck if low on cards
        if len(deck.cards) < 15:
            deck.build()
            deck.shuffle()

    print(f"Final bankroll: £{bankroll.amount}")


def determine_winner(player_hand, dealer_hand):
    """Determines the winner and prints the final result.

    Returns
    -------
    str
        "player" if the player wins, "dealer" if the dealer wins, or
        "push" in case of a tie.
    """
    player_value = player_hand.value
    dealer_value = dealer_hand.value

    print("\n--- Results ---")
    print(f"Your final hand: {player_hand} (Value: {player_value})")
    print(f"Dealer's final hand: {dealer_hand} (Value: {dealer_value})")

    if player_value > 21:
        # This case is handled in the player loop, but we keep it for clarity
        print("\033[91mYou busted! Dealer wins.\033[0m")
        return "dealer"
    if dealer_value > 21:
        print("\033[92mDealer busted! You win!\033[0m")
        return "player"
    if player_value > dealer_value:
        print("\033[92mCongratulations, you win!\033[0m")
        return "player"
    if dealer_value > player_value:
        print("\033[91mDealer wins!\033[0m")
        return "dealer"
    print("\033[93mIt's a push (a tie)!\033[0m")
    return "push"


if __name__ == "__main__":
    play_game()
