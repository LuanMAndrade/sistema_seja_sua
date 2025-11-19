from django.db import models


class FinanceSector(models.Model):
    """Configurable sectors for expense categorization"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Finance Sector"
        verbose_name_plural = "Finance Sectors"

    def __str__(self):
        return self.name


class FinanceInflow(models.Model):
    """
    Money inflows from Tiny ERP API (JSON)
    Cannot be edited manually - read-only from API
    """
    external_id = models.CharField(max_length=100, unique=True, help_text="ID from Tiny ERP")
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    sector = models.ForeignKey(
        FinanceSector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inflows'
    )

    # API sync tracking
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Finance Inflow (Tiny ERP)"
        verbose_name_plural = "Finance Inflows (Tiny ERP)"

    def __str__(self):
        return f"{self.description} - R$ {self.amount} ({self.date})"


class FinanceOutflow(models.Model):
    """
    Money outflows/expenses from Tiny ERP API (JSON)
    Cannot be edited manually - read-only from API
    """
    external_id = models.CharField(max_length=100, unique=True, help_text="ID from Tiny ERP")
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    sector = models.ForeignKey(
        FinanceSector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outflows'
    )

    # API sync tracking
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Finance Outflow (Tiny ERP)"
        verbose_name_plural = "Finance Outflows (Tiny ERP)"

    def __str__(self):
        return f"{self.description} - R$ {self.amount} ({self.date})"


class PredictedExpense(models.Model):
    """
    Predicted expenses calculated from Statistics module
    Auto-calculated, not manually entered
    """
    description = models.CharField(max_length=500)
    predicted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    predicted_date = models.DateField()
    sector = models.ForeignKey(
        FinanceSector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predicted_expenses'
    )
    confidence_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Confidence level (0-100%)",
        default=0
    )
    notes = models.TextField(blank=True, help_text="Calculation notes or assumptions")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-predicted_date', '-predicted_amount']
        verbose_name = "Predicted Expense"
        verbose_name_plural = "Predicted Expenses"

    def __str__(self):
        return f"{self.description} - R$ {self.predicted_amount} (Predicted: {self.predicted_date})"
