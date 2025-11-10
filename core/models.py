from django.db import models

# Create your models here.
import random
import string
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

# Create your models here.

class CustomUserManager(UserManager):
    # Basic user creation function
    def _create_user(self, email, password, **extra_fields):
        if not email: 
            raise ValueError("You have not provided a valid email")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # Creates a basic user and sets admin and superuser status to false
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
     # Creates a superuser and sets admin and superuser status to True
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)
    

# This is the custom user model that allows login and authentication with email and password
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, default='', unique=True)
    first_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_financeadmin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

# The .objects points to the CustomUserManager which contains the methods for user creation
    objects = CustomUserManager() 
# The username field from the default user is replaced with the email to allow for authentication via email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.first_name 

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
   

class UserProfile(models.Model):
    # One to one field with an existing user instance
    user = models.OneToOneField(User,primary_key=True, on_delete=models.CASCADE, related_name='user_profile')
    # Choices for dropdown in the various selections. Passed to html template view
    body_shape_choices = [
        ("Hourglass", "Hourglass"),
        ("Rectangle", "Rectangle"),
        ("Apple", "Apple"),
        ("Pear", "Pear"),
        ("Inverted Traingle", "Inverted Traingle"),
    ]
    chest = models.CharField(max_length=250)
    waist_circumference = models.CharField(max_length=250)
    hip_circumference = models.CharField(max_length=250)
    Inseam_length = models.CharField(max_length=250)
    height = models.CharField(max_length=250)
    weight = models.CharField(max_length=250, blank=True, null=True, default=None) 
    # weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=None) 
    body_shape = models.CharField(max_length=255, default='', choices=body_shape_choices)
    image = models.ImageField(upload_to='images', blank=True, null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
    




# | Measurement                    | Applies To      | Why It’s Needed                                                                                    |
# | ------------------------------ | --------------- | -------------------------------------------------------------------------------------------------- |
# | Chest / Bust circumference | Tops, Outerwear | Main determinant of fit for shirts, hoodies, jackets — directly comparable to garment chest width. |
# | Waist circumference        | Tops, Bottoms   | Critical for both shirt taper and pant sizing.                                                     |
# | Hip circumference          | Bottoms         | Needed for pants, skirts, or fitted dresses to assess lower-body fit.                              |
# | Inseam length              | Bottoms         | Needed to recommend correct pant length (short/regular/long).                                      |
# | Height                     | All             | Used as context for proportions; helps refine recommendation if multiple fits are similar.         |