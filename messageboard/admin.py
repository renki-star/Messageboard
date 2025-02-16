from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('username', 'text', 'timestamp', 'approved')
    list_filter = ('approved',)
    actions = ['approve_messages']

    def approve_messages(self, request, queryset):
        queryset.update(approved=True)
    approve_messages.short_description = "Hyväksy valitut viestit"

admin.site.register(Message, MessageAdmin)
