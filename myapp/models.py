from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from datetime import date, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta

cat = (
    ('normal', 'normal'),
    ('mixed', 'mixed'),
)
sex = (
    ('male', 'male'),
    ('female', 'female'),
    ('both', 'both'),
)
STATUS_CHOICES = (
    (False, 'Pending'),
    (True, 'Approved'),
)
DOSE_CHOICES = (
    (0, 'Pending dose'),
    (1, 'First dose'),
    (2, 'Second dose'),
    (3, 'Yearly dose'),
    (4, 'Pending yearly dose'),
)
STATUS_AI = [
    (True, 'Pregnant'),
    (False, 'Not Pregnant'),
    (None, 'Pending Pregnancy'),
]


VACCINATION_SCHEDULES = {
    'Anthrax': 365,  # days between vaccinations
    'Blackleg': 180,
    'LumpySkinDisease': 365,
    'BovinePateurollosis': 180,
    'FootAndMouth': 365,
}


# User model
class User(AbstractUser):
    is_admin= models.BooleanField('Is admin', default=False)
    is_farmer = models.BooleanField('Is farmer', default=False)
    is_vet = models.BooleanField('Is vet', default=False)

    def __str__(self):
        return self.username


# Farmer model
class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile', null=True)
    name = models.CharField(max_length=255, default="Unknown Farmer")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, default="0000000000")

    def __str__(self):
        return self.name

# Vet model
class Vet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vet_profile', null=True)
    name = models.CharField(max_length=255, default="Unknown Vet")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name



# Cattle model
class Cattle(models.Model):
    tagno = models.CharField(max_length=12, unique=True)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    dob = models.DateField(default=date.today)
    age_months = models.IntegerField(default=0)
    age_years = models.IntegerField(default=0)
    weight = models.IntegerField()
    color=models.CharField(max_length=50)
    owner = models.ForeignKey(Farmer, on_delete=models.CASCADE, default=1)

    def save(self, *args, **kwargs):
        if self.dob:
            today = date.today()
            age_in_months = (today.year - self.dob.year) * 12 + (today.month - self.dob.month)
            self.age_months = age_in_months
            self.age_years = age_in_months // 12
        super(Cattle, self).save(*args, **kwargs)

    def __str__(self):
        return self.tagno
    

class CattleProductionStage(models.Model):
    cattle = models.OneToOneField('Cattle', on_delete=models.CASCADE, related_name='production_stage')
    stage_choices = [
        ('calf', 'Calf (0-6 months)'),
        ('heifer', 'Heifer (6-24 months)'),
        ('dry', 'Dry Cow'),
        ('early_lactation', 'Early Lactation (0-100 days)'),
        ('mid_lactation', 'Mid Lactation (100-200 days)'),
        ('late_lactation', 'Late Lactation (200+ days)'),
    ]
    stage = models.CharField(max_length=20, choices=stage_choices, default='calf')
    milk_production = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="kg/day")
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.cattle.tagno} - {self.get_stage_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-set the stage based on age if not explicitly set
        if not self.stage or self.stage == 'calf' or self.stage == 'heifer':
            # Auto determine stage based on age and gender
            if self.cattle.age_months <= 6:
                self.stage = 'calf'
            elif self.cattle.age_months <= 24:
                self.stage = 'heifer'
            elif self.cattle.gender.lower() == 'female':
                # Default adult female to dry if not specified
                self.stage = 'dry'
        
        super().save(*args, **kwargs)

from dateutil.relativedelta import relativedelta
# Cattle record model
class CattleRecord(models.Model):
    tagno = models.ForeignKey(Cattle, on_delete=models.CASCADE, to_field='tagno')
    breed = models.CharField(max_length=50, default='Unknown Breed')
    gender = models.CharField(max_length=50, default='Unknown Gender')
    dob = models.DateField(default=date.today)
    vaccination_type = models.CharField(max_length=50)
    last_vaccination_date = models.DateField()
    next_vaccination_due = models.DateField(null=True, blank=True)
    age_months = models.IntegerField(default=0)
    age_years = models.IntegerField(default=0)
    observation = models.TextField()
    disease_diagnosis = models.TextField()
    weight = models.FloatField()
    color=models.CharField(max_length=50, default='Unknown Color')

    def __str__(self):
        return f"Cattle Tag {self.tagno}"
    
    def save(self, *args, **kwargs):
        # Auto calculate age
        if self.dob:
            today = date.today()
            rdelta = relativedelta(today, self.dob)
            self.age_years = rdelta.years
            self.age_months = rdelta.months
        
        # Set next vaccination due date if not provided
        if not self.next_vaccination_due and self.last_vaccination_date:
            # Get interval based on vaccination type or default to 180 days
            days_interval = int(VACCINATION_SCHEDULES.get(self.vaccination_type, 180))
            self.next_vaccination_due = self.last_vaccination_date + timedelta(days=days_interval)
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Cattle Records"

    def get_next_vaccination_due_formatted(self):
        """
        Returns the next vaccination due date as a formatted string,
        or an empty string if it's None.
        """
        if self.next_vaccination_due:
            return self.next_vaccination_due.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        else:
            return ""

    def get_last_vaccination_date_formatted(self):
        """
        Returns the last vaccination date as a formatted string,
        """
        return self.last_vaccination_date.strftime("%Y-%m-%d")
        


# Vaccination model
class Vaccination(models.Model):
    
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    vaccine = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Vaccination for {self.cattle.tagno} by {self.vet.name} on {self.date}"
 

class Appointment(models.Model):
    vet = models.ForeignKey(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=100, default='fname')
    lname = models.CharField(max_length=100, default='lname')
    email = models.EmailField()
    mobile = models.CharField(max_length=15, default=0000000000)
    request_details = models.TextField(default='request')
    status = models.CharField(max_length=20, default='Pending')  # Pending, Approved, Rejected 
    appointment_date = models.DateField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    accepted_date = models.DateTimeField(null=True, blank=True) 
    
    def __str__(self):
        return f"{self.fname} {self.lname}"


