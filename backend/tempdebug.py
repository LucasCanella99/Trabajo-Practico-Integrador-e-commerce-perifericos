from models.cart import Cart
from models.product import Product
from models.user import User

# Acá voy a estar probando el código que funcione como es esperado 

# Creo dos productos distintos
product1 = Product(175, "Teclado Corsair", 100000, 9)
product2 = Product(200, "Mouse Logitech", 30000, 6)

# Creo un usuario
user1 = User("Manolo", "manolete@email.com")
user2 = User("Antonio", "antoniete@email.com")

# Creo dos carritos y les asigno dueño
cart1 = Cart(user1)
cart2 = Cart(user2)

# Manolo y Antonio añaden productos a sus carritos
cart1.add_product(product1, 8)
cart2.add_product(product2, 5)

print(cart1.items)    
print(cart2.items)
print(product1, product2, user1, user2, cart1, cart2)
