from django.db import models
from django.contrib.auth.models import User


# =========================
# CORE MODELS
# =========================

class County(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Constituency(models.Model):
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE,
        related_name='constituencies'
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.county.name})"


class LevelOfStudy(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# =========================
# APPLICATION MODEL
# =========================

class Application(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    LEVEL_CHOICES = (
        ('university', 'University'),
        ('college', 'College'),
        ('kmtc', 'KMTC'),
        ('high', 'High School'),
    )

    # Student & application details
    student_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='applications'
    )
    full_name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=50)  # unique removed to fix migration error
    school = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    phone = models.CharField(max_length=20)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)

    # Location and level
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='applications')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='applications')
    level_of_study = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    # Supporting documents
    document = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.admission_number}"


# =========================
# CONSTITUENCY ADMIN
# =========================

class ConstituencyOfficer(models.Model):
    """
    One user → one constituency ONLY
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    constituency = models.OneToOneField(Constituency, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ({self.constituency.name})"
