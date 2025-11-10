from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for the User model (email-only authentication).
    """

    # Fields to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')

    # Fieldsets control layout when viewing/editing a user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fields shown when creating a new user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_email', 'chest', 'waist_circumference', 'hip_circumference', 'height', 'body_shape')
    list_filter = ('body_shape',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Body Measurements (inches)', {
            'fields': ('chest', 'waist_circumference', 'hip_circumference', 'Inseam_length', 'height', 'weight')
        }),
        ('Body Type', {
            'fields': ('body_shape',)
        }),
        ('Profile Photo', {
            'fields': ('image',)
        }),
    )
    
    # Custom method to display user email in list view
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    # Make the form more user-friendly
    autocomplete_fields = []  # Add if you have many users
    
    # Display image preview in admin
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 200px; max-width: 200px;" />'
        return "No image uploaded"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True