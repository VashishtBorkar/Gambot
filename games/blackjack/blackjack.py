from .deck import Deck
from ..hand import Hand

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
    def __init__(self):
        self.deck = Deck()
        self.dealer = BlackjackHand()
        self.player = BlackjackHand()

    def deal_hand(self):
        self.dealer.add_card(self.deck.draw_card())
        hidden_card = self.deck.draw_card()
        hidden_card.hide()
        self.dealer.add_card(hidden_card)


        self.player.add_card(self.deck.draw_card())
        self.player.add_card(self.deck.draw_card())

        if self.player.is_blackjack():
            if self.dealer.is_blackjack():
                return "push"
            else:
                return "blackjack"
        
        return "continue"

    def hit(self):
        self.player.add_card(self.deck.draw_card())

        if self.player.is_bust():
            return "dealer"
        
        if self.player.get_total() == 21:
            return self.stay()

        return "continue"

    def stay(self):
        self.dealer.reveal_hidden()

        while self.dealer.get_total() < 17:
            self.dealer.add_card(self.deck.draw_card())
        
        return self.check_winner()
    
    def can_double_down(self):
        return len(self.player.cards) == 2 and not self.doubled_down
    
    def double_down(self):
        if not self.can_double_down():
            raise ValueError("Cannot double down at this stage.")

        self.player.add_card(self.deck.draw())
        self.doubled_down = True
        return self.stay()

    def check_winner(self):
        if self.dealer.is_bust():
            return "player"
        if self.player.is_bust():
            return "dealer"
        
        dealer_total = self.dealer.get_total()
        player_total = self.player.get_total()

        if dealer_total > player_total:
            return "dealer"
        if dealer_total < player_total:
            return "player"
        if dealer_total == player_total:
            return "push"
    def reset(self):
        self.deck = Deck()
        self.dealer = BlackjackHand()
        self.player = BlackjackHand()
