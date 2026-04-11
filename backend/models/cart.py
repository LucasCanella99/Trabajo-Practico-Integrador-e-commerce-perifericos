class CartItem:
    def __init__(self, product, amount):
        self.product = product
        self.amount = amount

class Cart:
    def __init__(self, owner):
        self.owner = owner
        self.items = [] 

    def add_product(self, product, amount):
        if amount <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        
        for item in self.items: # Buscar si el producto ya está en el carrito
            if item.product.id == product.id:
                if item.amount + amount > product.stock: # Verificar stock disponible
                    raise ValueError("No hay stock disponible para agregar esa cantidad.")
                
                item.amount += amount
                return
        
        if amount > product.stock:
            raise ValueError("No hay stock disponible para agregar esa cantidad.")

        self.items.append(CartItem(product, amount))

