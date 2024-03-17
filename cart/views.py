from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .cart import Cart
from store.models import *
from django.contrib.auth.decorators import login_required
import uuid
from decimal import Decimal
from .telegram import main
import asyncio
import tempfile


data = {
    
}

def cart_summary(request):
    cart = Cart(request)
    cart_prods = cart.get_products()
    prod_count = cart.get_quantity()
    all_price = cart.get_price()
    total = cart.get_total()
    data = {
        'cart_prods': cart_prods,
        'prod_count': prod_count,
        'all_price': all_price,
        'total': total
    }
    return render(request, 'cart/cart_summary.html', context=data)

def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = request.POST.get('product_id')
        prod_count = request.POST.get('prod_count')
        product = get_object_or_404(Product, id=product_id)
        if int(prod_count) > 0: cart.add(product=product, quantity=prod_count)
        else: cart.add(product=product_id, quantity=0)
        cart_items = cart.__len__()
        return JsonResponse({"cart_items": cart_items, 'quantity': cart_items})  
    return render(request, 'store/index.html')

def detail_cart(request, pk):
    cart = Cart(request)
    cart_prods = cart.get_products()
    prod_count = cart.get_quantity()
    all_price = cart.get_price()
    data = {
        'cart_prods': cart_prods,
        'prod_count': prod_count,
        'all_price': all_price
    }
    product = get_object_or_404(Product, id=pk)
    data['product'] = product
    return render(request, 'cart/product.html', context=data)

def cart_update(request):
    try:
        cart = Cart(request)
        if request.POST.get('action')=='post':
            product_id = request.POST.get('product_id')
            prod_count = request.POST.get('prod_count')
            if int(prod_count) > 0: cart.update(product_id=product_id, quantity=prod_count)
            else: cart.update(product_id=product_id, quantity=0)
            return JsonResponse({'success': True})
        return render(request, 'cart/product.html', context=data)
    except:
        return HttpResponse('Quantity is must be positive integer!')

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = request.POST.get('product_id')
        cart.delete(product_id=product_id)
        return JsonResponse({'success': True})
    return render(request, 'cart/product.html')


def send_telegram(data, order_id):
    message = f"Yangi buyurtma: Buyurtma raqami: {order_id}:\n"
    i = 0
    for info in data:
        i+=1
        message += f"{i}. Mahsulot nomi: {info['name']}\n"
        message += f"\t\t  Id: {info['id']}\n"
        message += f"\t\t  Name: {info['name']}\n"
        message += f"\t\t  Price: {info['price']}\n"
        message += f"\t\t  Quantity: {info['quantity']}\n"
        message += f"\t\t  Total Price: {info['all_price']}\n\n"
    return message


@login_required
def order_details(request):
    cart = Cart(request)
    all_info = cart.get_all_info()
    if request.user.id is None:
        return HttpResponseRedirect(reverse('login'))
    else:
        order = Order()
        order.user_id = request.user
        order.order_id = uuid.uuid4()
        order_id = order.order_id
        order.total_price = cart.get_total()
        order.save()

        for info in all_info:
            order_item = OrderItem(
                order = order,
                product_id = int(info["id"]),
                name = info["name"],
                price = Decimal(info["price"]),
                quantity = int(info["quantity"]),
                all_price = Decimal(info["all_price"])
            )
            order_item.save()

        asyncio.run(main(send_telegram(all_info, order_id)))
        receipt_file = create_receipt(all_info, order_id)
        info = write_info(receipt_file, order_id)
        cart.cart_clear()
        return info


def create_receipt(order_info, order_id):
    with tempfile.NamedTemporaryFile(delete=False, mode='w+') as file:
        file.write(f"Yangi buyurtma: Buyurtma raqami: {order_id}:\n")
        i = 0
        for info in order_info:
            i+=1
            file.write(f"{i}. Mahsulot nomi: {info['name']}\n")
            file.write(f"\tId: {info['id']}\n")
            file.write(f"\tName: {info['name']}\n")
            file.write(f"\tPrice: {info['price']}\n")
            file.write(f"\tQuantity: {info['quantity']}\n")
            file.write(f"\tTotal Price: {info['all_price']}\n\n")
        file_path = file.name
    return file_path    

def write_info(file_path, order_id):
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename=order_{order_id}.txt'
        return response
     
@login_required
def order_info(request):
    orders = Order.objects.filter(user_id=request.user) 
    data = {}
    result = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        result1 = {'order': order.order_id, 'items': order_items, "total": order.total_price}
        result.append(result1)
    data['orders'] = result
    return render(request, 'cart/orders.html', context=data)
