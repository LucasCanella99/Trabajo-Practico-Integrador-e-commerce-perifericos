from django.contrib import admin
from apps.users.models import User
from django.contrib.auth.models import Group
# Register your models here.

admin.site.register(User)

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass