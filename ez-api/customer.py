from itsdangerous import TimedSerializer
class Customer(object):
    def __init__(self, email, password):
        self.email=email
        self.password=password
        self.balance=0
        sel.customer_id=None #make a random generator

    def increaseBalance(self,amount):
        self.balance+=amount