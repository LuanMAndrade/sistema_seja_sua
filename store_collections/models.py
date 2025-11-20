from django.db import models
from business_settings.models import Supplier, PieceCategory


class Fabric(models.Model):
    """Fabric materials for pieces"""
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=100)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='fabrics')
    roll_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight of roll in kg")
    yield_area_per_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area per kg (m²/kg)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'color']

    def __str__(self):
        return f"{self.name} - {self.color}"


class Collection(models.Model):
    """Clothing collections"""
    STATUS_CHOICES = [
        ('awaiting_modeler', 'Awaiting Modeler'),
        ('awaiting_pilot', 'Awaiting Pilot Maker'),
        ('awaiting_production', 'Awaiting Production'),
        ('released', 'Released'),
    ]

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='awaiting_modeler')
    notes = models.TextField(blank=True)
    expected_launch_date = models.DateField(null=True, blank=True)
    actual_launch_date = models.DateField(null=True, blank=True)

    # Collection-specific deadlines (overrides from BusinessDeadlines)
    modeling_time = models.PositiveIntegerField(help_text="Days for modeling")
    pilot_piece_time = models.PositiveIntegerField(help_text="Days for pilot piece")
    test_piece_time = models.PositiveIntegerField(help_text="Days for test piece")
    production_time = models.PositiveIntegerField(help_text="Days for production")
    preparation_time = models.PositiveIntegerField(help_text="Days for preparation")
    transportation_time = models.PositiveIntegerField(help_text="Days for transportation")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_launch_date(self):
        """Returns actual launch date if available, otherwise expected"""
        return self.actual_launch_date if self.actual_launch_date else self.expected_launch_date


class Piece(models.Model):
    """Individual pieces within a collection"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    SIZE_CHOICES = [
        ('P', 'P'),
        ('M', 'M'),
        ('G', 'G'),
        ('GG', 'GG'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nome", default='Sem Nome', blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='pieces')
    category = models.ForeignKey(PieceCategory, on_delete=models.PROTECT)
    fabric = models.ForeignKey(Fabric, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    # Fabric consumption per size (in square meters or similar unit)
    fabric_consumption_p = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fabric Consumption P")
    fabric_consumption_m = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fabric Consumption M")
    fabric_consumption_g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fabric Consumption G")
    fabric_consumption_gg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fabric Consumption GG")

    # Initial quantity per size
    initial_quantity_p = models.PositiveIntegerField(default=0, verbose_name="Initial Quantity P")
    initial_quantity_m = models.PositiveIntegerField(default=0, verbose_name="Initial Quantity M")
    initial_quantity_g = models.PositiveIntegerField(default=0, verbose_name="Initial Quantity G")
    initial_quantity_gg = models.PositiveIntegerField(default=0, verbose_name="Initial Quantity GG")

    # Tiny ERP Integration
    tiny_erp_piece = models.ForeignKey(
        'inventory.InventoryPiece',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_pieces',
        help_text="Link to Tiny ERP inventory piece for stock sync"
    )

    # Current stock (synced from Tiny ERP)
    current_stock_p = models.PositiveIntegerField(default=0, verbose_name="Current Stock P")
    current_stock_m = models.PositiveIntegerField(default=0, verbose_name="Current Stock M")
    current_stock_g = models.PositiveIntegerField(default=0, verbose_name="Current Stock G")
    current_stock_gg = models.PositiveIntegerField(default=0, verbose_name="Current Stock GG")
    stock_last_synced = models.DateTimeField(null=True, blank=True, help_text="Last time stock was synced from Tiny ERP")

    accessories = models.ManyToManyField('inventory.InventoryAccessory', blank=True, related_name='pieces')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['collection', 'category']

    def __str__(self):
        return f"{self.name} ({self.collection.name})"

    @property
    def margin(self):
        """Calculate profit margin: (sale_price - cost) / sale_price"""
        if self.sale_price > 0:
            return ((self.sale_price - self.total_cost) / self.sale_price) * 100
        return 0

    @property
    def total_initial_quantity(self):
        """Total pieces across all sizes"""
        return (
            self.initial_quantity_p +
            self.initial_quantity_m +
            self.initial_quantity_g +
            self.initial_quantity_gg
        )

    @property
    def total_current_stock(self):
        """Total current stock across all sizes"""
        return (
            self.current_stock_p +
            self.current_stock_m +
            self.current_stock_g +
            self.current_stock_gg
        )

    @property
    def is_synced_with_tiny(self):
        """Check if this piece is linked to Tiny ERP"""
        return self.tiny_erp_piece is not None


class PieceColor(models.Model):
    """Colors available for a piece"""
    piece = models.ForeignKey(Piece, on_delete=models.CASCADE, related_name='colors')
    color_name = models.CharField(max_length=100)
    color_hex = models.CharField(max_length=7, blank=True, help_text="Hex color code (e.g., #FF5733)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['piece', 'color_name']

    def __str__(self):
        return f"{self.piece} - {self.color_name}"


class PieceImage(models.Model):
    """Modeling images for pieces (can be uploaded multiple times)"""
    piece = models.ForeignKey(Piece, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pieces/modeling/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.piece} - Image {self.id}"
