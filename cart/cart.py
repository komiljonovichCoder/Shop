from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session

        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        prod_count = str(quantity)

        if product_id in self.cart: 
            pass
        else: 
            self.cart[product_id] = prod_count 
        self.session.modified = True

    def __len__(self):
        return len(self.cart)
    
    def get_products(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products
    
    def get_quantity(self):
        return self.cart
    
    def update(self, product_id, quantity):
        self.cart[product_id] = quantity
        self.session.modified = True 
        return self.cart

    def delete(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True

    def get_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total = 0
        for key, value in self.cart.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.sale_price: total += int(value)*product.sale_price
                    else: total += int(value)*product.price
        return total
    
    def get_price(self):
        all_price = {}
        try:
            for key, value in self.cart.items():
                prod = Product.objects.get(id=key)
                value = int(value)  
                all_price[key] = prod.price * value
            return all_price
        except ValueError:
            for key, value in self.cart.items():
                prod = Product.objects.get(id=key)
                value = int(value)  
                all_price[key] = f"{prod.name}'s quantity is must be positive integer!"
            return all_price
        
    def get_all_info(self):
        products = self.get_products()
        quantity = self.get_quantity()
        all_prod_price = self.get_price()
        total = self.get_total()
        result = []

        for prod in products:
            if str(prod.id) in quantity:
                data = {
                    "id": prod.id,
                    "name": str(prod.name),
                    "price": prod.price,
                    "quantity": quantity[str(prod.id)],
                    "all_price": all_prod_price[str(prod.id)]
                }
                result.append(data)
        return result
    
    def cart_clear(self):
        self.cart.clear()
        self.session.modified = True
        return self.cart
            