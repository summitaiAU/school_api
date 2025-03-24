from django.contrib import admin
from rest_framework.authtoken.models import Token

@admin.register(Token)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created')
    fields = ('user',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only when creating a new token
            # Save the object first to generate a key
            super().save_model(request, obj, form, change)
            # Store the key temporarily for display in the message
            obj._key_displayed_once = obj.key
        else:
            super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # Show the token in the success message only once
        if hasattr(obj, '_key_displayed_once'):
            key_value = obj._key_displayed_once
            message = f"IMPORTANT: Your API token has been created. Please copy it now as it will never be shown again: {key_value}"
            from django.contrib import messages
            messages.add_message(request, messages.WARNING, message)
        return super().response_add(request, obj, post_url_continue)
    
    def has_change_permission(self, request, obj=None):
        # Tokens can't be edited, only created or deleted
        return False