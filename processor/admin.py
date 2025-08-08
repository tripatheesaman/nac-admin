from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import ProcessedFile, StaffDetails

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(ProcessedFile)
class ProcessedFileAdmin(admin.ModelAdmin):
    """Admin for ProcessedFile model"""
    list_display = ('filename', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('original_file', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'original_file', 'processed_file', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StaffDetails)
class StaffDetailsAdmin(admin.ModelAdmin):
    """Admin for StaffDetails model"""
    list_display = ('staffid', 'name', 'section', 'designation', 'type_of_employment', 'level', 'priority')
    list_filter = ('section', 'type_of_employment', 'weekly_off', 'level')
    search_fields = ('staffid', 'name', 'section', 'designation')
    ordering = ('staffid',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'staffid', 'name', 'section', 'designation')
        }),
        ('Employment Details', {
            'fields': ('type_of_employment', 'level', 'priority', 'weekly_off')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at') 