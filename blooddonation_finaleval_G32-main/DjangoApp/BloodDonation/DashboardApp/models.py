from django.db import models
from django.conf import settings
from django.utils import timezone

class BloodDonation(models.Model):
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("O+", "O+"), ("O-", "O-"),
        ("AB+", "AB+"), ("AB-", "AB-")
    ]

    CITY_CHOICES = [
        ("Delhi", "Delhi"),
        ("Mumbai", "Mumbai"),
        ("Chandigarh", "Chandigarh"),
        ("Rajpura", "Rajpura"),
        ("Ludhiana", "Ludhiana"),
        ("Bathinda", "Bathinda"),
        ("Patiala", "Patiala"),
    ]

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    email = models.EmailField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    amount = models.FloatField()
    donation_date = models.DateTimeField(default=timezone.now)
    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    weight = models.FloatField()
    age = models.IntegerField()

    def __str__(self):
        return f"{self.donor.name} donated {self.amount} pints of {self.blood_group} blood"


class DonationCamp(models.Model):
    camp_name = models.CharField(max_length=255)
    CITY_CHOICES = [
        ("Delhi", "Delhi"),
        ("Mumbai", "Mumbai"),
        ("Chandigarh", "Chandigarh"),
        ("Rajpura", "Rajpura"),
        ("Ludhiana", "Ludhiana"),
        ("Bathinda", "Bathinda"),
        ("Patiala", "Patiala"),
    ]
    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    organizer_name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = BloodDonation.BLOOD_GROUP_CHOICES
    CITY_CHOICES = BloodDonation.CITY_CHOICES

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    quantity_needed = models.FloatField(default=1.0)
    requested_on = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.requester.name} requested {self.quantity_needed} pints of {self.blood_group}"
