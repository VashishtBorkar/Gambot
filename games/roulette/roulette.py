import random 

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
    def __init__(self):
        self.wheel = RouletteWheel()
        self.number, self.color = None, None
    
    def get_bet_type(self, bet):
        if str.isdigit(bet) and 0 <= int(bet) <= 36:
            return "number"
        elif bet in ["green", "black", "red"]:
            return "color"
        elif bet in ["odd", "even"]:
            return "parity"
        else:
            return "invalid"
        
    def get_spin(self):
        return self.number, self.color

    def play_round(self, bets, amount):
        self.number, self.color = self.wheel.spin()
        total_result = 0

        for bet in bets:
            bet_type = self.get_bet_type(bet)
            
            if bet_type == "number" and self.number == int(bet):
                total_result += amount * 36
            elif bet_type == "color" and self.color == bet:
                total_result += amount * 2
            elif bet_type == "parity" and self.number != 0:
                if (self.number % 2 == 0 and bet == "even") or \
                   (self.number % 2 == 1 and bet == "odd"):
                    total_result += amount * 2

        return total_result
    
    