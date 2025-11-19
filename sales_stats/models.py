from django.db import models
from store_collections.models import Piece, Collection, Fabric


class SalesData(models.Model):
    """
    Historical sales data from Tiny ERP API
    Read-only - synced from external API
    """
    external_id = models.CharField(max_length=100, unique=True, help_text="ID from Tiny ERP")
    sale_date = models.DateField()
    piece_sku = models.CharField(max_length=100, help_text="SKU of the piece sold")
    piece_name = models.CharField(max_length=200)
    quantity_sold = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Size breakdown (if available)
    quantity_p = models.PositiveIntegerField(default=0, verbose_name="Quantity P")
    quantity_m = models.PositiveIntegerField(default=0, verbose_name="Quantity M")
    quantity_g = models.PositiveIntegerField(default=0, verbose_name="Quantity G")
    quantity_gg = models.PositiveIntegerField(default=0, verbose_name="Quantity GG")

    # API sync tracking
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']
        verbose_name = "Sales Data (Tiny ERP)"
        verbose_name_plural = "Sales Data (Tiny ERP)"

    def __str__(self):
        return f"{self.piece_name} - {self.quantity_sold} units ({self.sale_date})"


class PieceSalesStatistics(models.Model):
    """
    Aggregated statistics for individual pieces
    Auto-calculated from SalesData
    """
    piece = models.OneToOneField(Piece, on_delete=models.CASCADE, related_name='sales_statistics')

    # Sales metrics
    total_units_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Size breakdown
    total_sold_p = models.PositiveIntegerField(default=0, verbose_name="Total Sold P")
    total_sold_m = models.PositiveIntegerField(default=0, verbose_name="Total Sold M")
    total_sold_g = models.PositiveIntegerField(default=0, verbose_name="Total Sold G")
    total_sold_gg = models.PositiveIntegerField(default=0, verbose_name="Total Sold GG")

    # Performance metrics
    first_sale_date = models.DateField(null=True, blank=True)
    last_sale_date = models.DateField(null=True, blank=True)
    days_since_launch = models.PositiveIntegerField(default=0)

    # Tracking
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Piece Sales Statistics"
        verbose_name_plural = "Piece Sales Statistics"

    def __str__(self):
        return f"Stats: {self.piece} ({self.total_units_sold} sold)"


class CollectionSalesStatistics(models.Model):
    """
    Aggregated statistics for collections
    Auto-calculated from piece statistics
    """
    collection = models.OneToOneField(Collection, on_delete=models.CASCADE, related_name='sales_statistics')

    # Sales metrics
    total_units_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_piece_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pieces_in_collection = models.PositiveIntegerField(default=0)

    # Performance
    best_selling_piece_name = models.CharField(max_length=200, blank=True)
    worst_selling_piece_name = models.CharField(max_length=200, blank=True)
    collection_launch_date = models.DateField(null=True, blank=True)

    # Tracking
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Collection Sales Statistics"
        verbose_name_plural = "Collection Sales Statistics"

    def __str__(self):
        return f"Stats: {self.collection} ({self.total_units_sold} sold)"


class FabricSalesStatistics(models.Model):
    """
    Aggregated statistics for fabrics
    Auto-calculated from piece statistics
    """
    fabric = models.OneToOneField(Fabric, on_delete=models.CASCADE, related_name='sales_statistics')

    # Usage metrics
    total_pieces_using_fabric = models.PositiveIntegerField(default=0)
    total_units_sold = models.PositiveIntegerField(default=0, help_text="Total pieces sold using this fabric")
    total_fabric_consumed_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total fabric consumed in kg"
    )

    # Revenue
    total_revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Tracking
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fabric Sales Statistics"
        verbose_name_plural = "Fabric Sales Statistics"

    def __str__(self):
        return f"Stats: {self.fabric} ({self.total_units_sold} pieces sold)"


class SalesForecast(models.Model):
    """
    Sales forecasts calculated using data science (NumPy, Pandas, SciPy)
    Auto-generated predictions
    """
    FORECAST_TYPES = [
        ('piece', 'Piece Forecast'),
        ('collection', 'Collection Forecast'),
        ('fabric', 'Fabric Forecast'),
        ('overall', 'Overall Forecast'),
    ]

    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPES)
    target_name = models.CharField(max_length=200, help_text="Name of piece/collection/fabric being forecasted")

    # Forecast data
    forecast_date = models.DateField(help_text="Date for which forecast is made")
    predicted_units = models.PositiveIntegerField(default=0)
    predicted_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    confidence_interval_lower = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    confidence_interval_upper = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    confidence_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Confidence level (0-100%)",
        default=0
    )

    # Methodology
    model_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Statistical model used (e.g., Linear Regression, ARIMA)"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the forecast")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-forecast_date', '-created_at']
        verbose_name = "Sales Forecast"
        verbose_name_plural = "Sales Forecasts"

    def __str__(self):
        return f"{self.forecast_type}: {self.target_name} ({self.forecast_date})"
