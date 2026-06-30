from django.contrib import admin

from .models import ContactInfo, ContactMessage, UserProfile

admin.site.register(UserProfile)
admin.site.register(ContactInfo)
admin.site.register(ContactMessage)
