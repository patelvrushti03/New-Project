from django.contrib import admin

from .models import ContactInfo, ContactMessage, CustomUser

admin.site.register(CustomUser)
admin.site.register(ContactInfo)
admin.site.register(ContactMessage)
