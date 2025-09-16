from django.contrib import admin

# Register your models here.
# core/admin.py
from django.contrib import admin
from .models import User, Bet, Ticket

admin.site.register(User)
admin.site.register(Bet)
admin.site.register(Ticket)
