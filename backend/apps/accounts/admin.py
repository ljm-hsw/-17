from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Card, CardActivationCode, CardBinding, User

admin.site.register(User, UserAdmin)
admin.site.register(Card)
admin.site.register(CardActivationCode)
admin.site.register(CardBinding)
