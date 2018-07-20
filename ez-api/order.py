import Item
class Order(object):
    def __init__(self,customer_id,items_amount = None):
        self.customer_id=customer_id
        if items_amount is not None:
            self.items_amount=items_amount
        else:
            self.items_amount = {}
        self.total=None

    def calculateTotal(self):
        total = 0
        for item , amount in items_amount.items():
            total+= item.price*amount
        self.total=total