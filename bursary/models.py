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

    # Location
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True)
    level_of_study = models.ForeignKey(LevelOfStudy, on_delete=models.SET_NULL, null=True)

    # Personal
    full_name = models.CharField(max_length=200)
    id_no = models.CharField(max_length=20)
    birth_cert_no = models.CharField(max_length=50, blank=True, null=True)
    identity_document = models.FileField(upload_to='documents/')
    gender = models.CharField(max_length=10)
    disability = models.CharField(max_length=5)
    disability_type = models.CharField(max_length=100, blank=True, null=True)
    disability_document = models.FileField(upload_to='documents/', blank=True, null=True)

    # Education
    admission_number = models.CharField(max_length=50)
    school = models.CharField(max_length=200)
    course = models.CharField(max_length=200)
    year_of_study = models.CharField(max_length=20)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    document = models.FileField(upload_to='documents/')
    performance = models.CharField(max_length=20)
    transcript = models.FileField(upload_to='documents/')

    # Geo
    polling_station = models.CharField(max_length=200)
    sub_location = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    ward = models.CharField(max_length=200)

    # Family
    family_status = models.CharField(max_length=50)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_occupation = models.CharField(max_length=200, blank=True, null=True)
    father_id = models.CharField(max_length=20, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_occupation = models.CharField(max_length=200, blank=True, null=True)
    mother_id = models.CharField(max_length=20, blank=True, null=True)
    father_death_no = models.CharField(max_length=50, blank=True, null=True)
    father_death_doc = models.FileField(upload_to='documents/', blank=True, null=True)
    mother_death_no = models.CharField(max_length=50, blank=True, null=True)
    mother_death_doc = models.FileField(upload_to='documents/', blank=True, null=True)
    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_occupation = models.CharField(max_length=200, blank=True, null=True)

    # Siblings (comma-separated)
    siblings_names = models.TextField(blank=True, null=True)
    siblings_amounts = models.TextField(blank=True, null=True)

    # Referees
    referee1_name = models.CharField(max_length=200)
    referee1_phone = models.CharField(max_length=20)
    referee2_name = models.CharField(max_length=200)
    referee2_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

# =========================
# CONSTITUENCY OFFICER
# =========================
class ConstituencyOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    constituency = models.OneToOneField(Constituency, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ({self.constituency.name})"
