import random
from card import Card

class Deck:
    def __init__(self, seed=42):
        random.seed(seed)

    def draw_card(self):
        suit = random.choice(Card.suits)
        rank = random.choice(Card.ranks)
        return Card(rank, suit)
    
if __name__ == "__main__":
    deck = Deck(42)
    for i in range(10):
        card = deck.draw_card()  
        print(f"Card {i+1}: {card} (value: {card.get_value()})")


    
