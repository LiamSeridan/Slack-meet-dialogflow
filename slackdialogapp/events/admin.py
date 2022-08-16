from django.contrib import admin
from .models import slackuser, dialogflowintent

admin.site.register(slackuser)
admin.site.register(dialogflowintent)

# Register your models here.
