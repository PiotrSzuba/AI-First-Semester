from dataclasses import dataclass
from typing import Tuple, List, Dict, Set
import uuid

class Item:
    id: str
    name: str
    price: float
    
    def __init__(self, name: str, price: float) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price

@dataclass
class Cart:
    items: List[Item]
    
    def add_item(self, item: Item) -> None:
        self.items.append(item)
        
    def get_total_price(self) -> float:
        total_price = 0.0
        for item in self.items:
            total_price += item.price
        return total_price
    
    def clear_cart(self) -> None:
        self.items.clear()
        
    def buy_all(self) -> float:
        total_price = 0.0
        items_count = len(self.items)
        
        for i in range(items_count):
            total_price += self.items[i].price
        
        self.clear_cart()
        
        return total_price

    def get_unique_items(self) -> Set[str]:
        names = [x.name for x in self.items]
        return set(names)
    
    def get_item_names(self) -> List[str]:
        if (len(self.items) >= 0):
            names = list(map(lambda x: x.name, self.items))
            return names
        else:
            return []
        

class User:
    id: str
    name: str
    password: str
    cart: Cart
    
    def __init__(self, name: str, password: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.password = password
        self.cart = Cart([])
        
    def add_item_to_cart(self, item: Item) -> bool:
        self.cart.add_item(item)
        
    def get_user_login_info(self) -> Tuple[str, str]:
        return (self.name, self.password)

@dataclass
class UserManager:
    users: Dict[str, bool]
    
    def sign_up(self, user: User) -> bool:
        if (self.users.get(user.name) != None):
            return False
        
        self.users[user.name] = False
        
        return True
    
    def sign_in(self, user: User) -> bool:
        if (self.users.get(user.name) == None):
            return False
        
        if (self.users[user.name] == True):
            return False
        
        self.users[user.name] = True
        
        return True
    
    def sign_out(self, user: User) -> bool:
        if (self.users.get(user.name) == None):
            return False
        
        if (self.users[user.name] == False):
            return False
        
        self.users[user.name] = False
        
        return True
        
def main():
    user_manager = UserManager(dict())
    user = User("PSZ", 1234)
    
    sign_in = user_manager.sign_in(user)
    sign_out = user_manager.sign_out(user)
    sign_up = user_manager.sign_up(user)
    print("Could sign in ?: ", sign_in)
    print("Could sign out ?: ", sign_out)
    print("Could sign up ?: ", sign_up)
    sign_out = user_manager.sign_out(user)
    sign_in = user_manager.sign_in(user)
    print("Could sign out ?: ", sign_out)
    print("Could sign in ?: ", sign_in)
    sign_in = user_manager.sign_in(user)
    print("Could sign in ?: ", sign_in)
    sign_out = user_manager.sign_out(user)
    print("Could sign out ?: ", sign_out)
    
    item = Item('cola', 5.99)
    user.add_item_to_cart(item)
    user.add_item_to_cart(item)
    print("All items in cart: ", user.cart.get_item_names())
    print("Unique items in cart: ", user.cart.get_unique_items())
    print(user.cart.buy_all())
    print("Items in cart after buy: ", len(user.cart.items))

if __name__ == "__main__":
    main()