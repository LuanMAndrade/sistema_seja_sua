from django.contrib import admin
from .models import MarketingCampaign, SocialMediaPost, PromotionalMaterial


class SocialMediaPostInline(admin.TabularInline):
    model = SocialMediaPost
    extra = 0
    fields = ['platform', 'status', 'scheduled_date', 'caption']
    show_change_link = True


class PromotionalMaterialInline(admin.TabularInline):
    model = PromotionalMaterial
    extra = 0
    fields = ['name', 'material_type', 'file']
    show_change_link = True


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'campaign_type',
        'status',
        'start_date',
        'end_date',
        'budget',
        'actual_spend',
        'created_by'
    ]
    search_fields = ['name', 'description']
    list_filter = ['campaign_type', 'status', 'start_date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    filter_horizontal = ['collections', 'pieces']
    inlines = [SocialMediaPostInline, PromotionalMaterialInline]

    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'campaign_type', 'status', 'description')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Associated Content', {
            'fields': ('collections', 'pieces')
        }),
        ('Budget', {
            'fields': ('budget', 'actual_spend')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = [
        'platform',
        'status',
        'scheduled_date',
        'scheduled_time',
        'campaign',
        'likes',
        'comments',
        'shares',
        'views'
    ]
    search_fields = ['caption', 'hashtags']
    list_filter = ['platform', 'status', 'scheduled_date', 'campaign']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
    filter_horizontal = ['collections', 'pieces']

    fieldsets = (
        ('Post Information', {
            'fields': ('campaign', 'platform', 'status')
        }),
        ('Content', {
            'fields': ('caption', 'hashtags', 'image', 'link_url')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time', 'published_date')
        }),
        ('Engagement Metrics', {
            'fields': ('likes', 'comments', 'shares', 'views'),
            'classes': ('collapse',)
        }),
        ('Associated Content', {
            'fields': ('collections', 'pieces'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PromotionalMaterial)
class PromotionalMaterialAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'material_type',
        'campaign',
        'created_at'
    ]
    search_fields = ['name', 'description']
    list_filter = ['material_type', 'campaign', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    filter_horizontal = ['collections', 'pieces']

    fieldsets = (
        ('Material Information', {
            'fields': ('name', 'material_type', 'description', 'campaign')
        }),
        ('Files', {
            'fields': ('file', 'thumbnail')
        }),
        ('Associated Content', {
            'fields': ('collections', 'pieces'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
