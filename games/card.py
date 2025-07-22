class Card:
    suit_symbols = {
        "spades": "♠️",
        "hearts": "♥️",
        "diamonds": "♦️",
        "clubs": "♣️"
    }

    suits = list(suit_symbols.keys())
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    card_values = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    
    def __init__(self, rank, suit, face_down=False):
        if suit not in self.suits:
            raise ValueError(f"Invalid suit: {suit}")
        if rank not in self.ranks:
            raise ValueError(f"Invalid rank: {rank}")
        
        self.rank = rank
        self.suit = suit # store as full name, e.g. "spades"
        self.face_down = face_down

    def __str__(self):
        return "XX" if self.face_down else f"{self.rank}{self.suit_symbols[self.suit]}"
    
    def show(self):
        self.face_down = False
    
    def hide(self):
        self.face_down = True
    
    def get_value(self):
        return self.card_values[self.rank]

