import uuid

from django.db import models
from rest_framework.exceptions import ValidationError


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee'

    def is_responsible_for(self, organization):
        return OrganizationResponsible.objects.filter(organization_id=organization, user_id=self).exists()

    def is_responsible_for_any_organization(self):
        return OrganizationResponsible.objects.filter(user=self).exists()
class Organization(models.Model):

    class OrganizationType(models.TextChoices):
        IE = 'IE'
        LLC = 'LLC'
        JSC = 'JSC'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(choices=OrganizationType.choices)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'organization'

    def get_responsible_count(self):
        return OrganizationResponsible.objects.filter(organization_id=self).count()





class OrganizationResponsible(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE, blank=True, null=True, db_column='organization_id')
    user = models.ForeignKey(Employee, models.CASCADE, blank=True, null=True, db_column='user_id')

    class Meta:
        managed = False
        db_table = 'organization_responsible'


class Tender(models.Model):

    class StatusType(models.TextChoices):
        Created = 'Created'
        Published = 'Published'
        Closed = 'Closed'


    class ServiceType(models.TextChoices):
        Construction = 'Construction'
        Delivery = 'Delivery'
        Manufacture = 'Manufacture'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    serviceType = models.CharField(choices=ServiceType.choices)
    status = models.CharField(choices=StatusType.choices)
    createdAt = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1)
    organization_id = models.ForeignKey(Organization, models.CASCADE)
    creator_id = models.ForeignKey(Employee, models.CASCADE)

    def clean(self):
        if self.status not in dict(self.StatusType.choices):
            raise ValidationError({'status': 'Invalid status value.'})
        if self.serviceType not in dict(self.ServiceType.choices):
            raise ValidationError({'serviceType': 'Invalid serviceType value.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_bid_authors(self):
        return Employee.objects.filter(bid__tenderId=self).distinct()


class TenderVersion(models.Model):
    class StatusType(models.TextChoices):
        Created = 'Created'
        Published = 'Published'
        Closed = 'Closed'

    class ServiceType(models.TextChoices):
        Construction = 'Construction'
        Delivery = 'Delivery'
        Manufacture = 'Manufacture'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    serviceType = models.CharField(choices=ServiceType.choices)
    status = models.CharField(choices=StatusType.choices)
    createdAt = models.DateTimeField()
    version = models.PositiveIntegerField()
    organization_id = models.ForeignKey(Organization, models.CASCADE)
    creator_id = models.ForeignKey(Employee, models.CASCADE)

    def clean(self):
        if self.status not in dict(self.StatusType.choices):
            raise ValidationError({'status': 'Invalid status value.'})
        if self.serviceType not in dict(self.ServiceType.choices):
            raise ValidationError({'serviceType': 'Invalid serviceType value.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Bid(models.Model):

    class StatusType(models.TextChoices):
        Created = 'Created'
        Published = 'Published'
        Canceled = 'Canceled'
        Approved = 'Approved'
        Rejected = 'Rejected'


    class AuthorType(models.TextChoices):
        Organization = 'Organization'
        User = 'User'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(choices=StatusType.choices)
    tenderId = models.ForeignKey(Tender, on_delete=models.CASCADE)
    authorType = models.CharField(choices=AuthorType.choices)
    authorId = models.ForeignKey(Employee, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    createdAt = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.status not in dict(self.StatusType.choices):
            raise ValidationError({'status': 'Invalid status value.'})
        if self.authorType not in dict(self.AuthorType.choices):
            raise ValidationError({'authorType': 'Invalid authorType value.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class BidVersion(models.Model):
    class StatusType(models.TextChoices):
        Created = 'Created'
        Published = 'Published'
        Canceled = 'Canceled'
        Approved = 'Approved'
        Rejected = 'Rejected'

    class AuthorType(models.TextChoices):
        Organization = 'Organization'
        User = 'User'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(choices=StatusType.choices)
    tenderId = models.ForeignKey(Tender, on_delete=models.CASCADE)
    authorType = models.CharField(choices=AuthorType.choices)
    authorId = models.ForeignKey(Employee, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    createdAt = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.status not in dict(self.StatusType.choices):
            raise ValidationError({'status': 'Invalid status value.'})
        if self.authorType not in dict(self.AuthorType.choices):
            raise ValidationError({'authorType': 'Invalid authorType value.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BidReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(max_length=500)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    author = models.ForeignKey(Employee, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

class BidDecision(models.Model):

    class DecisionType(models.TextChoices):
        Approved = 'Approved'
        Rejected = 'Rejected'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    author = models.ForeignKey(Employee, on_delete=models.CASCADE)
    decision = models.CharField(choices=DecisionType.choices)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bid', 'author'], name='unique_biddecision')
        ]

    def clean(self):
        if self.decision not in dict(self.DecisionType.choices):
            raise ValidationError({'status': 'Invalid decision value.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)