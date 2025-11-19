from django.db import models
from django.contrib.auth.models import User
from store_collections.models import Collection, Piece


class MarketingCampaign(models.Model):
    """Marketing campaigns for collections and pieces"""
    CAMPAIGN_TYPES = [
        ('launch', 'Collection Launch'),
        ('promotion', 'Promotion'),
        ('sale', 'Sale'),
        ('social_media', 'Social Media'),
        ('email', 'Email Marketing'),
        ('influencer', 'Influencer Partnership'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    description = models.TextField(blank=True)

    # Date range
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    # Associated collections/pieces
    collections = models.ManyToManyField(Collection, blank=True, related_name='marketing_campaigns')
    pieces = models.ManyToManyField(Piece, blank=True, related_name='marketing_campaigns')

    # Budget
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = "Marketing Campaign"
        verbose_name_plural = "Marketing Campaigns"

    def __str__(self):
        return f"{self.name} ({self.campaign_type})"


class SocialMediaPost(models.Model):
    """Social media posts for marketing"""
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('twitter', 'Twitter/X'),
        ('pinterest', 'Pinterest'),
        ('youtube', 'YouTube'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    campaign = models.ForeignKey(
        MarketingCampaign,
        on_delete=models.CASCADE,
        related_name='social_posts',
        null=True,
        blank=True
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Content
    caption = models.TextField(help_text="Post caption/text")
    hashtags = models.TextField(blank=True, help_text="Hashtags (one per line)")
    image = models.ImageField(upload_to='marketing/posts/', blank=True)
    link_url = models.URLField(blank=True, help_text="Link in bio or post link")

    # Scheduling
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    # Engagement metrics (optional, can be filled in manually)
    likes = models.PositiveIntegerField(default=0, blank=True)
    comments = models.PositiveIntegerField(default=0, blank=True)
    shares = models.PositiveIntegerField(default=0, blank=True)
    views = models.PositiveIntegerField(default=0, blank=True)

    # Associated content
    collections = models.ManyToManyField(Collection, blank=True, related_name='social_posts')
    pieces = models.ManyToManyField(Piece, blank=True, related_name='social_posts')

    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date', '-created_at']
        verbose_name = "Social Media Post"
        verbose_name_plural = "Social Media Posts"

    def __str__(self):
        return f"{self.platform} - {self.status} ({self.scheduled_date or 'No date'})"


class PromotionalMaterial(models.Model):
    """Promotional materials and assets"""
    MATERIAL_TYPES = [
        ('banner', 'Banner'),
        ('flyer', 'Flyer'),
        ('brochure', 'Brochure'),
        ('catalog', 'Catalog'),
        ('video', 'Video'),
        ('photo', 'Photo'),
        ('lookbook', 'Lookbook'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    description = models.TextField(blank=True)

    # File
    file = models.FileField(upload_to='marketing/materials/', blank=True)
    thumbnail = models.ImageField(upload_to='marketing/thumbnails/', blank=True)

    # Campaign association
    campaign = models.ForeignKey(
        MarketingCampaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotional_materials'
    )

    # Collections/pieces featured
    collections = models.ManyToManyField(Collection, blank=True, related_name='promotional_materials')
    pieces = models.ManyToManyField(Piece, blank=True, related_name='promotional_materials')

    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Promotional Material"
        verbose_name_plural = "Promotional Materials"

    def __str__(self):
        return f"{self.name} ({self.material_type})"
