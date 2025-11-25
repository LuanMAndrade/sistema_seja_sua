from django.db import models


class Supplier(models.Model):
    """Suppliers for fabrics and accessories"""
    name = models.CharField(max_length=200)
    delivery_time_days = models.PositiveIntegerField(help_text="Delivery time in business days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.delivery_time_days} days)"


class PieceCategory(models.Model):
    """Categories for clothing pieces"""
    name = models.CharField(max_length=200)
    subcategory = models.CharField(max_length=200, blank=True, null=True)
    production_cost_per_piece = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo de Produção por Peça (R$)",
        help_text="Custo médio de produção por peça desta categoria"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'subcategory']
        verbose_name_plural = "Piece Categories"

    def __str__(self):
        if self.subcategory:
            return f"{self.name} - {self.subcategory}"
        return self.name


class BusinessDeadlines(models.Model):
    """Default deadlines for production processes (in business days)"""
    production_time = models.PositiveIntegerField(default=0)
    fabric_testing_time = models.PositiveIntegerField(default=0)
    modeling_time = models.PositiveIntegerField(default=0)
    pilot_piece_time = models.PositiveIntegerField(default=0)
    test_piece_for_production = models.PositiveIntegerField(default=0)
    preparation_time = models.PositiveIntegerField(default=0)
    transportation_time = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Business Deadlines"
        verbose_name_plural = "Business Deadlines"

    def __str__(self):
        return f"Default Business Deadlines (Updated: {self.updated_at.strftime('%Y-%m-%d')})"
