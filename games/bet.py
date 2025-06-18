from db.models import UserEconomy
from db.database import SessionLocal

class Bet:
    def __init__(self, user_id, amount):
        self.user_id = user_id
        self.amount = amount

        # Validate once at creation
        with SessionLocal() as session:
            user = session.query(UserEconomy).filter_by(user_id=user_id).first()

            if not user:
                raise ValueError("User does not exist.")

            if self.amount < 5:
                raise ValueError("Minimum bet is $5.")

            if self.amount > user.balance:
                raise ValueError("Insufficient funds.")

    def place(self):
        with SessionLocal() as session:
            user = session.query(UserEconomy).filter_by(user_id=self.user_id).first()
            if not user:
                raise ValueError("User does not exist")
            user.balance -= self.amount
            session.commit()

    def double(self):
        with SessionLocal() as session:
            user = session.query(UserEconomy).filter_by(user_id=self.user_id).first()
            if not user:
                raise ValueError("User does not exist")

            if user.balance < self.amount:
                raise ValueError("Insufficient funds to double down")

            user.balance -= self.amount
            session.commit()

        self.amount *= 2
    
    def get_bet_amount(self):
        return self.amount

    def payout(self, multiplier=1):
        winnings = int(self.amount * multiplier)

        with SessionLocal() as session:
            user = session.query(UserEconomy).filter_by(user_id=self.user_id).first()
            if not user:
                raise ValueError("User does not exist")
            user.balance += winnings
            session.commit()
        return winnings
    
    def payout_total(self, total_winnings):
        with SessionLocal() as session:
            user = session.query(UserEconomy).filter_by(user_id=self.user_id).first()
            if not user:
                raise ValueError("User does not exist")
            user.balance += total_winnings
            session.commit()
        return total_winnings
