from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import ProcessedFile, StaffDetails, Section, Department

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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter sections based on user access
        if self.user and not self.user.is_superuser:
            if self.user.department:
                self.fields['section'].queryset = Section.objects.filter(department=self.user.department, is_active=True)
            else:
                self.fields['section'].queryset = Section.objects.none()
        else:
            self.fields['section'].queryset = Section.objects.filter(is_active=True)
    
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
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
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


class SectionForm(forms.Form):
    """Form for section management"""
    
    def __init__(self, *args, **kwargs):
        self.section_id = kwargs.pop('section_id', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set department based on user access
        if self.user and not self.user.is_superuser:
            if self.user.department:
                # For regular users, set their department and make it read-only
                self.fields['department'].queryset = Department.objects.filter(id=self.user.department.id)
                self.fields['department'].initial = self.user.department
                self.fields['department'].required = False  # Not required since it's auto-set
                self.fields['department'].widget.attrs['readonly'] = True
                self.fields['department'].widget.attrs['disabled'] = True
            else:
                self.fields['department'].queryset = Department.objects.none()
        else:
            # Superusers can choose any department
            self.fields['department'].queryset = Department.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Handle disabled department field for regular users
        if self.user and not self.user.is_superuser and self.user.department:
            # If department field is disabled, use the user's department
            cleaned_data['department'] = self.user.department
        
        return cleaned_data
    
    def clean_department(self):
        department = self.cleaned_data.get('department')
        
        # For regular users with disabled department field, use their department
        if self.user and not self.user.is_superuser and self.user.department:
            if not department:  # Field was disabled and not in POST data
                return self.user.department
        
        return department
    
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Section Name'}),
        label="Section Name"
    )
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Section Code'}),
        label="Section Code"
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Department"
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Description'}),
        label="Description"
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Active"
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check if code already exists using raw SQL
            from django.db import connection
            with connection.cursor() as cursor:
                if self.section_id:
                    # Exclude current section when editing
                    cursor.execute("SELECT COUNT(*) FROM sections WHERE code = %s AND id != %s", [code, self.section_id])
                else:
                    # Check for any existing code when creating
                    cursor.execute("SELECT COUNT(*) FROM sections WHERE code = %s", [code])
                count = cursor.fetchone()[0]
                if count > 0:
                    raise forms.ValidationError("Section Code already exists")
        return code
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check if name already exists using raw SQL
            from django.db import connection
            with connection.cursor() as cursor:
                if self.section_id:
                    # Exclude current section when editing
                    cursor.execute("SELECT COUNT(*) FROM sections WHERE name = %s AND id != %s", [name, self.section_id])
                else:
                    # Check for any existing name when creating
                    cursor.execute("SELECT COUNT(*) FROM sections WHERE name = %s", [name])
                count = cursor.fetchone()[0]
                if count > 0:
                    raise forms.ValidationError("Section Name already exists")
        return name


class SectionFilterForm(forms.Form):
    """Form for filtering section records"""
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by name'})
    )
    code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by code'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),  # Will be set in view
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Active'), ('false', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 