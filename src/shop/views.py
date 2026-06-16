import json
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import MenuItem, Category, Order, OrderItem, ContactMessage


# ─────────────────────────────────────────────
# CART HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_cart(request):
    """
    Get the cart from the session.
    The session is like a temporary notepad Django keeps for each browser visitor.
    The cart is stored as a dictionary: { "item_id": quantity, ... }
    e.g. { "1": 2, "3": 1 }
    """
    return request.session.get('cart', {})


def save_cart(request, cart):
    """Save the cart back to the session."""
    request.session['cart'] = cart
    request.session.modified = True  # Tell Django the session changed


def get_cart_item_count(request):
    """Count total number of items (sum of all quantities)."""
    cart = get_cart(request)
    return sum(cart.values())


def get_cart_details(request):
    """
    Build a full cart with item objects and totals.
    Returns a list of dicts with item info + quantity + subtotal.
    """
    cart = get_cart(request)
    cart_items = []
    total = Decimal('0.00')

    for item_id_str, quantity in cart.items():
        try:
            item = MenuItem.objects.get(pk=int(item_id_str))
            subtotal = item.price * quantity
            total += subtotal
            cart_items.append({
                'item': item,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except MenuItem.DoesNotExist:
            pass  # Item was deleted from the menu — skip it

    return cart_items, total


# ─────────────────────────────────────────────
# PAGE VIEWS
# ─────────────────────────────────────────────

def home(request):
    """
    The homepage.
    We fetch featured items (first 6 available items) to show in the grid.
    """
    featured_items = MenuItem.objects.filter(is_available=True)[:6]
    cart_count = get_cart_item_count(request)

    context = {
        'featured_items': featured_items,
        'cart_count': cart_count,
    }
    # render() takes: the request, the template path, and a context dictionary.
    # The context dictionary makes variables available inside the template.
    return render(request, 'shop/home.html', context)


def menu(request):
    """
    The full menu page.
    We fetch all categories and all available items.
    """
    categories = Category.objects.all()
    items = MenuItem.objects.filter(is_available=True).select_related('category')
    cart_count = get_cart_item_count(request)

    context = {
        'categories': categories,
        'items': items,
        'cart_count': cart_count,
    }
    return render(request, 'shop/menu.html', context)


def cart(request):
    """The cart page — shows all items the user has added."""
    cart_items, total = get_cart_details(request)
    cart_count = get_cart_item_count(request)

    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_count,
    }
    return render(request, 'shop/cart.html', context)


def checkout(request):
    """
    GET: Show the checkout form.
    POST: Process the form, create an Order, clear the cart.
    """
    cart_items, total = get_cart_details(request)

    if not cart_items:
        # If cart is empty, redirect back to the menu
        messages.warning(request, "Your cart is empty. Add some drinks first!")
        return redirect('menu')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()
        delivery_method = request.POST.get('delivery_method', 'pickup')
        address = request.POST.get('address', '').strip()

        if not customer_name or not contact_number:
            messages.error(request, "Please fill in your name and contact number.")
        else:
            # Create the Order
            order = Order.objects.create(
                customer_name=customer_name,
                contact_number=contact_number,
                delivery_method=delivery_method,
                address=address,
                total_price=total,
                session_key=request.session.session_key or '',
            )

            # Create an OrderItem for each item in the cart
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item['item'],
                    quantity=cart_item['quantity'],
                    price_at_order=cart_item['item'].price,
                )

            # Clear the cart
            request.session['cart'] = {}
            request.session.modified = True

            return redirect('order_success', order_id=order.pk)

    cart_count = get_cart_item_count(request)
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_count,
    }
    return render(request, 'shop/checkout.html', context)


def order_success(request, order_id):
    """Confirmation page shown after a successful order."""
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'shop/order_success.html', {'order': order, 'cart_count': 0})


def contact(request):
    """
    GET: Show the contact form.
    POST: Save the message and show a success notification.
    """
    cart_count = get_cart_item_count(request)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message_text,
            )
            messages.success(request, "Your message has been sent! We'll get back to you soon. ☕")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, 'shop/contact.html', {'cart_count': cart_count})


# ─────────────────────────────────────────────
# CART API VIEWS (called by JavaScript)
# ─────────────────────────────────────────────

@require_POST  # This decorator ensures only POST requests can call this view
def cart_add(request, item_id):
    """
    Add one item to the cart (or increase quantity).
    Called by JavaScript fetch() — returns JSON, not HTML.
    """
    item = get_object_or_404(MenuItem, pk=item_id, is_available=True)
    cart = get_cart(request)

    item_key = str(item_id)  # Session keys must be strings
    cart[item_key] = cart.get(item_key, 0) + 1
    save_cart(request, cart)

    cart_count = sum(cart.values())

    return JsonResponse({
        'success': True,
        'message': f'{item.name} added to cart!',
        'cart_count': cart_count,
        'item_quantity': cart[item_key],
    })


@require_POST
def cart_remove(request, item_id):
    """Remove an item from the cart entirely."""
    cart = get_cart(request)
    item_key = str(item_id)

    if item_key in cart:
        del cart[item_key]
        save_cart(request, cart)

    cart_count = sum(cart.values())
    return JsonResponse({'success': True, 'cart_count': cart_count})


@require_POST
def cart_update(request, item_id):
    """Update the quantity of an item in the cart."""
    cart = get_cart(request)
    item_key = str(item_id)

    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)

    if quantity <= 0:
        cart.pop(item_key, None)
    else:
        cart[item_key] = quantity

    save_cart(request, cart)
    cart_count = sum(cart.values())
    return JsonResponse({'success': True, 'cart_count': cart_count})


def cart_data(request):
    """Return cart as JSON — useful for JavaScript to read the current state."""
    cart = get_cart(request)
    cart_count = sum(cart.values())
    return JsonResponse({'cart': cart, 'cart_count': cart_count})