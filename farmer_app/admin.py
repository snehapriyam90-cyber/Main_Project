from django.contrib import admin
from .models import *


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('farm_name', 'verified_farmer', 'payout_enabled')
    list_filter = ('verified_farmer', 'payout_enabled')
