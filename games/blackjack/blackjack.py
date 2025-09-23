from ..deck import Deck
from ..hand import Hand
from ..card import Card

class BlackjackHand(Hand):
    def get_total(self):
        count = 0
        aces = 0

        for card in self.cards:
            if not card.face_down:
                count += card.get_value()
                if card.rank == "A":
                    aces += 1
        
        while count > 21 and aces > 0:
            count -= 10
            aces -= 1
        
        return count

    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_total() == 21

    def is_bust(self):
        return self.get_total() > 21
    
    def reveal_hidden(self):
        for card in self.cards:
            card.show()

    def __str__(self):
        return " -  ".join(str(card) for card in self.cards)
    
class Blackjack:
    def __init__(self, bet_amount=0):
        self.deck = Deck()
        self.dealer = BlackjackHand()
        self.player = BlackjackHand()
        self.doubled_down = False
        self.bet_amount = bet_amount
        self.game_over = False
        
        # Payout multipliers
        self.BLACKJACK_MULTIPLIER = 2.5
        self.WIN_MULTIPLIER = 2.0
        self.PUSH_MULTIPLIER = 1.0

    def get_game_state(self):
        """Returns current game state as a dictionary"""
        return {
            "game_over": self.game_over,
            "player_total": self.player.get_total(),
            "dealer_total": self.dealer.get_total(),
            "player_display": str(self.player),
            "dealer_display": str(self.dealer),
            "can_double_down": self.can_double_down(),
            "outcome": self._get_outcome(),
            "message": self._get_outcome_message(),
            "payout": self._calculate_payout()
        }

    def _get_outcome(self):
        """Determine the current game outcome"""
        if not self.game_over:
            return "in_progress"
        
        if self.player.is_blackjack() and not self.dealer.is_blackjack():
            return "blackjack"
        elif self.player.is_blackjack() and self.dealer.is_blackjack():
            return "push"
        elif self.player.is_bust():
            return "dealer_wins"
        elif self.dealer.is_bust():
            return "player_wins"
        elif self.dealer.get_total() > self.player.get_total():
            return "dealer_wins"
        elif self.dealer.get_total() < self.player.get_total():
            return "player_wins"
        else:
            return "push"

    def _get_outcome_message(self):
        """Get the display message for the outcome"""
        outcome = self._get_outcome()
        messages = {
            "blackjack": "🃏 Blackjack! You win!",
            "player_wins": "🎉 You win!",
            "dealer_wins": "💥 Dealer wins!",
            "push": "🤝 Push! It's a tie!",
            "in_progress": ""
        }
        return messages.get(outcome, "")

    def _calculate_payout(self):
        """Calculate the payout based on the outcome"""
        if not self.game_over:
            return 0
        
        outcome = self._get_outcome()
        multiplier = 0
        
        if outcome == "blackjack":
            multiplier = self.BLACKJACK_MULTIPLIER
        elif outcome == "player_wins":
            multiplier = self.WIN_MULTIPLIER
        elif outcome == "push":
            multiplier = self.PUSH_MULTIPLIER
        
        base_bet = self.bet_amount * 2 if self.doubled_down else self.bet_amount
        return base_bet * multiplier

    def deal_hand(self):
        """Deal initial hand and return game state"""
        self.dealer.add_card(self.deck.draw_card())
        hidden_card = self.deck.draw_card()
        hidden_card.hide()
        self.dealer.add_card(hidden_card)

        self.player.add_card(self.deck.draw_card())
        self.player.add_card(self.deck.draw_card())

        # Check for blackjack scenarios
        if self.player.is_blackjack():
            self.dealer.reveal_hidden()  # Reveal for blackjack check
            self.game_over = True

        return self.get_game_state()

    def hit(self):
        """Player takes a card"""
        if self.game_over:
            return self.get_game_state()
        
        self.player.add_card(self.deck.draw_card())

        if self.player.is_bust():
            self.game_over = True
        elif self.player.get_total() == 21:
            # Automatically stay on 21
            return self.stay()

        return self.get_game_state()

    def stay(self):
        """Player stays, dealer plays their hand"""
        if self.game_over:
            return self.get_game_state()
        
        self.dealer.reveal_hidden()

        while self.dealer.get_total() < 17:
            self.dealer.add_card(self.deck.draw_card())
        
        self.game_over = True
        return self.get_game_state()
    
    def can_double_down(self):
        """Check if player can double down"""
        return len(self.player.cards) == 2 and not self.doubled_down and not self.game_over
    
    def double_down(self):
        """Double down - double bet, take one card, then stay"""
        if not self.can_double_down():
            raise ValueError("Cannot double down at this stage.")

        self.doubled_down = True
        self.player.add_card(self.deck.draw_card())
        return self.stay()

    def reset(self):
        """Reset the game for a new round"""
        self.deck = Deck()
        self.dealer = BlackjackHand()
        self.player = BlackjackHand()
        self.doubled_down = False
        self.game_over = False

    def to_dict(self):
        return {
            "dealer": [card.to_dict() for card in self.dealer.cards],
            "player": [card.to_dict() for card in self.player.cards],
            "doubled_down": self.doubled_down,
            "bet_amount": self.bet_amount,
            "game_over": self.game_over
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(bet_amount=data["bet_amount"])

        obj.dealer = BlackjackHand()
        for card_data in data["dealer"]:
            obj.dealer.add_card(Card.from_dict(card_data))

        obj.player = BlackjackHand()
        for card_data in data["player"]:
            obj.player.add_card(Card.from_dict(card_data))

        obj.doubled_down = data["doubled_down"]
        obj.game_over = data["game_over"]

        return obj