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
    admission_number = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=(('Male','Male'),('Female','Female')), null=True, blank=True)
    id_no = models.CharField(max_length=50, blank=True, null=True)
    birth_no = models.CharField(max_length=50, blank=True, null=True)
    id_copy = models.FileField(upload_to='documents/id/', blank=True, null=True)
    birth_copy = models.FileField(upload_to='documents/birth/', blank=True, null=True)
    disability = models.BooleanField(default=False)
    disability_details = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20)

    # Educational details
    reg_no = models.CharField(max_length=50, blank=True, null=True)
    school = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    annual_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fee_structure = models.FileField(upload_to='documents/fee_structure/', blank=True, null=True)
    academic_performance = models.CharField(max_length=20, choices=(('Excellent','Excellent'),('Very Good','Very Good'),('Good','Good'),('Fair','Fair'),('Poor','Poor')), blank=True, null=True)
    transcript = models.FileField(upload_to='documents/transcript/', blank=True, null=True)

    # Location and level
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='applications')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='applications')
    level_of_study = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    # Geo details
    polling_station = models.CharField(max_length=255, blank=True, null=True)
    sub_location = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    ward = models.CharField(max_length=255, blank=True, null=True)

    # Family details
    parents_status = models.CharField(max_length=50, choices=(('both_alive','Both Alive'),('mother_alive','Mother Alive'),('father_alive','Father Alive'),('single_mother','Single Mother'),('single_father','Single Father'),('orphan','Orphan')), blank=True, null=True)
    parent_disabled = models.BooleanField(default=False)
    disabled_parent_name = models.CharField(max_length=255, blank=True, null=True)
    disabled_parent_phone = models.CharField(max_length=20, blank=True, null=True)
    disabled_parent_type = models.CharField(max_length=255, blank=True, null=True)
    disabled_parent_doc = models.FileField(upload_to='documents/disabled_parent/', blank=True, null=True)

    # Siblings
    siblings_highschool_names = models.TextField(blank=True, null=True)
    siblings_highschool_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    siblings_college_names = models.TextField(blank=True, null=True)
    siblings_college_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    siblings_university_names = models.TextField(blank=True, null=True)
    siblings_university_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Referees
    referee1_name = models.CharField(max_length=255, blank=True, null=True)
    referee1_phone = models.CharField(max_length=20, blank=True, null=True)
    referee2_name = models.CharField(max_length=255, blank=True, null=True)
    referee2_phone = models.CharField(max_length=20, blank=True, null=True)

    # Supporting documents
    document = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.admission_number}"

# =========================
# CONSTITUENCY OFFICER
# =========================
class ConstituencyOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    constituency = models.OneToOneField(Constituency, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ({self.constituency.name})"
