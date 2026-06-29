from django.contrib import admin

from .models import Contact, Users

admin.site.register(Users)
admin.site.register(Contact)
