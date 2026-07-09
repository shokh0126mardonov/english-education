from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Organization(TenantMixin):
    name = models.CharField('Organization name', max_length=255)
    created_on = models.DateField('Created on', auto_now_add=True)
    is_active = models.BooleanField('Is active', default=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'

    def __str__(self):
        return self.domain
