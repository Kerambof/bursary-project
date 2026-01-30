from django.db import models

class Application(models.Model):
    full_name = models.CharField(max_length=100)
    admission_number = models.CharField(max_length=50)
    school = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    year_of_study = models.IntegerField()
    phone = models.CharField(max_length=15)
    amount_requested = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
