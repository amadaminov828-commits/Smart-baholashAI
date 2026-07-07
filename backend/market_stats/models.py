from django.db import models
import json


class MarketStat(models.Model):
    """Cached market statistics from real scraping results."""
    CATEGORY_CHOICES = [
        ('vehicle', 'Vehicle'),
        ('real_estate', 'Real Estate'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    item_name = models.CharField(max_length=100)  # Model name or Property type
    avg_price = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    trend = models.CharField(max_length=20, default="+0.0%")
    region = models.CharField(max_length=100, default="Barchasi")
    scrape_source = models.CharField(max_length=50, default="olx", help_text="olx, avtoelon, combined")
    data_json = models.TextField(default="{}", help_text="Raw scraped listings as JSON")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Unique constraint to prevent duplicate entries
        unique_together = ['category', 'item_name', 'region', 'scrape_source']

    def __str__(self):
        return f"{self.item_name} ({self.region}) - {self.avg_price}"

    def get_listings(self):
        """Return parsed JSON listings."""
        try:
            return json.loads(self.data_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_listings(self, listings):
        """Save listings as JSON."""
        self.data_json = json.dumps(listings, ensure_ascii=False, default=str)


class DailyTrend(models.Model):
    """Daily snapshot for tracking trends over time."""
    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=20)
    region = models.CharField(max_length=100, default="Barchasi")
    avg_price = models.FloatField(default=0)
    listings_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['date', 'category', 'region']

    def __str__(self):
        return f"{self.date} - {self.category} ({self.region}): {self.listings_count} listings"


class StatsCache(models.Model):
    """Full API response cache — avoids re-scraping within cache duration."""
    cache_key = models.CharField(max_length=100, unique=True)  # e.g. "general_uz", "vehicles_uz_toshkent"
    response_json = models.TextField(default="{}")
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cache: {self.cache_key} ({self.created_at})"

    def get_data(self):
        try:
            return json.loads(self.response_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_data(self, data):
        self.response_json = json.dumps(data, ensure_ascii=False, default=str)
