from django.db import models


class Emmission(models.Model):
    co2e = models.FloatField(null=False, db_index=True)
    scope = models.IntegerField(null=False, db_index=True)
    category = models.IntegerField(null=True, default=None, db_index=True)
    activity = models.TextField(null=False)

    class Meta:
        index_together = (("scope", "category", "co2e"),)


class EmmissionFactor(models.Model):
    activity = models.TextField(null=False)
    lookup_identifier = models.TextField(null=False)
    unit = models.CharField(null=False, max_length=100)
    co2e_factor = models.FloatField(null=False)
    scope = models.IntegerField(null=False)
    category = models.IntegerField(null=True, default=None)

    class Meta:
        unique_together = (("activity", "lookup_identifier"),)
        index_together = (("activity", "lookup_identifier"),)
