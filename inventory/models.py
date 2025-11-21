from django.db import models


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
