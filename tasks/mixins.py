from django.db import models


class TrackingMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderingMixin(models.Model):
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
