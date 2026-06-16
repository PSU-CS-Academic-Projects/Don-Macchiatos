from django.db import models


class Category(models.Model):
    """
    Groups menu items together.
    Examples: Coffee, Matcha, Fruit Drinks
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # URL-friendly version, e.g. "iced-coffee"

    class Meta:
        verbose_name_plural = "Categories"  # Fix the admin panel label (not "Categorys")

    def __str__(self):
        # This controls how the object shows up in the admin panel
        return self.name


class MenuItem(models.Model):
    """
    A single drink on the menu.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # If the category is deleted, set this field to null
        null=True,
        blank=True,
        related_name='items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # blank=True means it's optional
    price = models.DecimalField(max_digits=6, decimal_places=2)  # e.g. 9999.99
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Set automatically on creation

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    A customer's order.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]

    customer_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup')
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)  # Links order to browser session

    def __str__(self):
        return f"Order #{self.pk} — {self.customer_name}"

    def calculate_total(self):
        """Add up all the items in this order."""
        total = sum(item.subtotal() for item in self.items.all())
        self.total_price = total
        self.save()
        return total


class OrderItem(models.Model):
    """
    One line in an order. E.g., "2x Iced Caramel Macchiato"
    An Order can have many OrderItems.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=6, decimal_places=2)  # Lock in the price

    def subtotal(self):
        return self.quantity * self.price_at_order

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"


class ContactMessage(models.Model):
    """
    A message submitted through the Contact page.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} — {self.submitted_at.strftime('%Y-%m-%d')}"