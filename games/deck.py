import random
from .card import Card

class Deck:
    def __init__(self, seed=None):
        if seed is not None:
            self.rng = random.Random(seed)
        else:
            self.rng = random  # Use system randomness by default

    def draw_card(self):
        suit = self.rng.choice(Card.suits)
        rank = self.rng.choice(Card.ranks)
        return Card(rank, suit)
    
if __name__ == "__main__":
    deck = Deck(42)
    for i in range(10):
        card = deck.draw_card()  
        print(f"Card {i+1}: {card} (value: {card.get_value()})")


    
