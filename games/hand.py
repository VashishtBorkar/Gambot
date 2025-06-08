class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def clear(self):
        self.cards = []

    def show(self):
        return ", ".join(str(card) for card in self.cards)
