from django.db import models


class InventoryPiece(models.Model):
    """
    Pieces pulled from Tiny ERP API (JSON)
    Cannot be edited manually - read-only from API
    """
    external_id = models.CharField(max_length=100, unique=True, help_text="ID from Tiny ERP")
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(default=0, help_text="Total quantity (sum of all sizes)")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Variant stock by size (for products with size variations)
    has_variations = models.BooleanField(default=False, help_text="True if product has size variations")
    stock_p = models.IntegerField(default=0, help_text="Stock for size P")
    stock_m = models.IntegerField(default=0, help_text="Stock for size M")
    stock_g = models.IntegerField(default=0, help_text="Stock for size G")
    stock_gg = models.IntegerField(default=0, help_text="Stock for size GG")

    # Store variations JSON for reference
    variations_data = models.JSONField(null=True, blank=True, help_text="Raw variations data from Tiny ERP")

    # API sync tracking
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Inventory Piece (Tiny ERP)"
        verbose_name_plural = "Inventory Pieces (Tiny ERP)"

    def __str__(self):
        return f"{self.name} - {self.quantity} units"


class InventoryAccessory(models.Model):
    """Accessories for inventory management"""
    name = models.CharField(max_length=200)
    minimum_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_days = models.PositiveIntegerField(help_text="Delivery time in business days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Inventory Accessory"
        verbose_name_plural = "Inventory Accessories"

    def __str__(self):
        return f"{self.name} (Min: {self.minimum_quantity})"


class Packaging(models.Model):
    """Packaging materials for inventory"""
    name = models.CharField(max_length=200)
    minimum_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_days = models.PositiveIntegerField(help_text="Delivery time in business days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Packaging"
        verbose_name_plural = "Packaging"

    def __str__(self):
        return f"{self.name} (Min: {self.minimum_quantity})"


class Gift(models.Model):
    """Gifts for inventory"""
    name = models.CharField(max_length=200)
    minimum_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_days = models.PositiveIntegerField(help_text="Delivery time in business days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Min: {self.minimum_quantity})"
