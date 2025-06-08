from deck import Deck
from hand import Hand

class BlackJackHand(Hand):
    def get_total(self):
        count = 0
        aces = 0

        for card in self.cards:
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
    
class BlackJack:
    def __init__(self, seed):
        self.deck = Deck(seed)
        self.dealer = BlackJackHand()
        self.player = BlackJackHand()

    def deal_hand(self):
        self.dealer.add_card(self.deck.draw_card())
        self.dealer.add_card(self.deck.draw_card().hide())

        self.player.add_card(self.deck.draw_card())
        self.player.add_card(self.deck.draw_card())

        if self.player.is_blackjack():
            if self.dealer.is_blackjack():
                return "push"
            else:
                return "player"
        
        return "continue"

    def hit(self):
        self.player.append(self.deck.draw_card())

        if self.player.is_bust():
            return "dealer"
        
        return "continue"

    def stay(self):
        self.dealer.reveal_hidden()

        while self.dealer.get_total() < 17:
            self.dealer.add_card(self.deck.draw_card)
        
        return self.check_winner()

    def check_winner(self):
        if self.dealer.is_bust():
            return "player"
        
        dealer_total = self.dealer.get_total()
        player_total = self.player.get_total()

        if dealer_total > player_total:
            return "dealer"
        
        if dealer_total < dealer_total:
            return "player"
        
        if dealer_total == player_total:
            return "push"
        
