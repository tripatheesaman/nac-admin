from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
import os


class Department(models.Model):
    """Model to store department information"""
    name = models.CharField(max_length=255, unique=True, verbose_name="Department Name")
    code = models.CharField(max_length=10, unique=True, verbose_name="Department Code")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']
        db_table = 'departments'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Section(models.Model):
    """Model to store section information"""
    name = models.CharField(max_length=255, unique=True, verbose_name="Section Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Section Code")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ['name']
        db_table = 'sections'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class CustomUserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, username, first_name, last_name, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, first_name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, first_name, last_name, email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with required fields"""
    # Override username to have a default value
    username = models.CharField(max_length=150, unique=True)
    
    # Required fields as specified
    first_name = models.CharField(max_length=150, verbose_name="First Name")
    last_name = models.CharField(max_length=150, verbose_name="Last Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    
    # Department field - null for superusers, required for regular users
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Department")
    
    # Additional fields for better user management
    is_active = models.BooleanField(default=True, verbose_name="Active")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Last Login")
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name


class ProcessedFile(models.Model):
    """Model to track processed Excel files"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Uploaded By", null=True, blank=True)
    original_file = models.FileField(upload_to='uploads/')
    processed_file = models.FileField(upload_to='processed/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Processed File"
        verbose_name_plural = "Processed Files"
    
    def __str__(self):
        return f"File {self.id} - {self.status}"
    
    def filename(self):
        return os.path.basename(self.original_file.name)
    
    def processed_filename(self):
        if self.processed_file:
            return os.path.basename(self.processed_file.name)
        return None


class StaffDetails(models.Model):
    """Model to store staff details"""
    WEEKLY_OFF_CHOICES = [
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thurs', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
    ]
    
    TYPE_OF_EMPLOYMENT_CHOICES = [
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('monthly wages', 'Monthly Wages'),
    ]
    
    staffid = models.CharField(max_length=255, unique=True, verbose_name="Staff ID")
    name = models.CharField(max_length=255, verbose_name="Full Name")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name="Section")
    designation = models.CharField(max_length=255, verbose_name="Designation")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department", null=True, blank=True)
    weekly_off = models.CharField(max_length=10, choices=WEEKLY_OFF_CHOICES, verbose_name="Weekly Off", default="sun")
    level = models.IntegerField(verbose_name="Level")
    type_of_employment = models.CharField(max_length=20, choices=TYPE_OF_EMPLOYMENT_CHOICES, verbose_name="Type of Employment", default="permanent")
    priority = models.IntegerField(verbose_name="Priority", default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Staff Detail"
        verbose_name_plural = "Staff Details"
        ordering = ['staffid']
        db_table = 'staff_details'
    
    def __str__(self):
        return f"{self.staffid} - {self.name}"
    
    def get_full_info(self):
        return f"{self.staffid} | {self.name} | {self.designation} | {self.section}"
