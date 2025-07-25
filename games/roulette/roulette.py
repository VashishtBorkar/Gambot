import random 
import discord

class RouletteWheel:
    RED = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    BLACK = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
    def __init__(self):
        self.numbers = list(range(37)) # 0-36

    def spin(self):
        result = random.choice(self.numbers)
        color = (
            "green" if result == 0 else
            "red" if result in self.RED else
            "black"
        )
        return result, color

class Roulette:
    def __init__(self, bets=None, bet_amount=0):
        self.wheel = RouletteWheel()
        self.bets = bets or []
        self.bet_amount = bet_amount
        self.spin_number = None
        self.spin_color = None
        
        # Payout multipliers
        self.NUMBER_MULTIPLIER = 36
        self.COLOR_MULTIPLIER = 2
        self.PARITY_MULTIPLIER = 2
        
        # Color display mapping
        self.color_emojis = {
            "red": "🔴",
            "black": "⚫",
            "green": "🟢"
        }
    
    def get_bet_type(self, bet):
        """Determine the type of bet made"""
        if str.isdigit(bet) and 0 <= int(bet) <= 36:
            return "number"
        elif bet.lower() in ["green", "black", "red"]:
            return "color"
        elif bet.lower() in ["odd", "even"]:
            return "parity"
        else:
            return "invalid"
        
    def validate_bets(self):
        """Validate all bets and return any invalid ones"""
        invalid_bets = []
        for bet in self.bets:
            if self.get_bet_type(bet) == "invalid":
                invalid_bets.append(bet)
        return invalid_bets
    
    def calculate_bet_winnings(self, bet):
        """Calculate winnings for a single bet"""
        bet_type = self.get_bet_type(bet)
        
        if bet_type == "number" and self.spin_number == int(bet):
            return self.bet_amount * self.NUMBER_MULTIPLIER
        elif bet_type == "color" and self.spin_color == bet.lower():
            return self.bet_amount * self.COLOR_MULTIPLIER
        elif bet_type == "parity" and self.spin_number != 0:
            is_even_bet = bet.lower() == "even"
            is_even_number = self.spin_number % 2 == 0
            if is_even_bet == is_even_number:
                return self.bet_amount * self.PARITY_MULTIPLIER
        
        return 0
    
    def get_winning_bets(self):
        """Get list of bets that won"""
        winning_bets = []
        for bet in self.bets:
            if self.calculate_bet_winnings(bet) > 0:
                winning_bets.append(bet)
        return winning_bets
    
    def get_game_state(self):
        """Return current game state as a dictionary"""
        total_bet = self.bet_amount * len(self.bets)
        total_winnings = sum(self.calculate_bet_winnings(bet) for bet in self.bets)
        net_gain = total_winnings - total_bet
        winning_bets = self.get_winning_bets()
        
        # Determine outcome message and embed color
        if net_gain > 0:
            outcome_message = "🤑 You won!"
            embed_color = discord.Color.green()
        elif net_gain < 0:
            outcome_message = "❌ You lost."
            embed_color = discord.Color.red()
        else:
            outcome_message = "⚖️ You broke even."
            embed_color = discord.Color.blurple()
        
        return {
            "bets": self.bets,
            "bet_amount": self.bet_amount,
            "total_bet": total_bet,
            "spin_number": self.spin_number,
            "spin_color": self.spin_color,
            "spin_display": f"{self.spin_number} {self.color_emojis.get(self.spin_color, self.spin_color)}" if self.spin_number is not None else "",
            "total_winnings": total_winnings,
            "net_gain": net_gain,
            "winning_bets": winning_bets,
            "outcome_message": outcome_message,
            "embed_color": embed_color,
            "game_complete": self.spin_number is not None
        }
        

    def play_round(self):
        """Play a complete roulette round"""
        # Validate bets first
        invalid_bets = self.validate_bets()
        if invalid_bets:
            raise ValueError(f"Invalid bets: {', '.join(invalid_bets)}")
        
        # Spin the wheel
        self.spin_number, self.spin_color = self.wheel.spin()
        
        # Return complete game state
        return self.get_game_state()

    def reset(self):
        """Reset the game for a new round"""
        self.spin_number = None
        self.spin_color = None
        self.bets = []
        self.bet_amount = 0
    
    