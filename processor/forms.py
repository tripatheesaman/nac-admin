from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import ProcessedFile, StaffDetails

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': ' '
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': ' '
        }),
        label="Password"
    )



class UserPasswordChangeForm(PasswordChangeForm):
    """Custom password change form"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        }),
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password'
        }),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password'
        }),
        label="Confirm New Password"
    )


class FileUploadForm(forms.ModelForm):
    """Form for file uploads"""
    class Meta:
        model = ProcessedFile
        fields = ['original_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_file'].widget.attrs.update({'id': 'file-upload'})

    def clean_original_file(self):
        file = self.cleaned_data.get('original_file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")
            
            # Check file extension
            allowed_extensions = ['.xls', '.xlsx', '.csv']
            file_extension = file.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Please upload an Excel file (.xls, .xlsx) or CSV file")
        
        return file


class ProcessingOptionsForm(forms.Form):
    """Form for processing options"""
    OUTPUT_CHOICES = [
        ('new', 'Create New File'),
        ('template', 'Use Template File'),
    ]
    
    output_type = forms.ChoiceField(
        choices=OUTPUT_CHOICES,
        initial='new',
        widget=forms.RadioSelect,
        help_text="Choose how to output the processed data"
    )
    
    template_file = forms.FileField(
        required=False,
        help_text="Upload a template file (optional)"
    )


class StaffDetailsForm(forms.Form):
    """Form for staff details management"""
    
    def __init__(self, *args, **kwargs):
        self.staff_id = kwargs.pop('staff_id', None)
        super().__init__(*args, **kwargs)
    
    staffid = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Staff ID'}),
        label="Staff ID"
    )
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Name'}),
        label="Full Name"
    )
    section = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Section'}),
        label="Section"
    )
    designation = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Designation'}),
        label="Designation"
    )
    weekly_off = forms.ChoiceField(
        choices=StaffDetails.WEEKLY_OFF_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Weekly Off"
    )
    level = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Level (1-10)'}),
        label="Level"
    )
    type_of_employment = forms.ChoiceField(
        choices=StaffDetails.TYPE_OF_EMPLOYMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type of Employment"
    )
    priority = forms.IntegerField(
        required=False,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Priority'}),
        label="Priority"
    )
    
    def clean_staffid(self):
        staffid = self.cleaned_data.get('staffid')
        if staffid:
            # Check if staffid already exists using raw SQL
            from django.db import connection
            with connection.cursor() as cursor:
                if self.staff_id:
                    # Exclude current staff member when editing
                    cursor.execute("SELECT COUNT(*) FROM staff_details WHERE staffid = %s AND id != %s", [staffid, self.staff_id])
                else:
                    # Check for any existing staffid when creating
                    cursor.execute("SELECT COUNT(*) FROM staff_details WHERE staffid = %s", [staffid])
                count = cursor.fetchone()[0]
                if count > 0:
                    raise forms.ValidationError("Staff ID already exists")
        return staffid
    
    def clean_level(self):
        level = self.cleaned_data.get('level')
        if level is not None and (level < 1 or level > 10):
            raise forms.ValidationError("Level must be between 1 and 10")
        return level
    
    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        if priority is None or priority == '':
            return 1  # Default value
        if priority < 0:
            raise forms.ValidationError("Priority must be a positive number")
        return priority


class StaffFilterForm(forms.Form):
    """Form for filtering staff records"""
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by name'})
    )
    staffid = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by Staff ID'})
    )
    section = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by section'})
    )
    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by designation'})
    )
    level = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Filter by level'})
    )
    weekly_off = forms.ChoiceField(
        choices=[('', 'All Days')] + StaffDetails.WEEKLY_OFF_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    type_of_employment = forms.ChoiceField(
        choices=[('', 'All Types')] + StaffDetails.TYPE_OF_EMPLOYMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Filter by priority'})
    ) 