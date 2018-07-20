class Item(object):
    def __init__(self, item_id, name, image, description, price):
        self.item_id=item_id
        self.name=name
        self.image=image #maybe make optional
        self.description=description #maybe make optional
        self.price=price