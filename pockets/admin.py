from django.contrib import admin

from .models import Pocket

class PocketAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']
    search_fields = ['summary', 'user__username', 'user__email']
    class Meta:
        model = Pocket

admin.site.register(Pocket, PocketAdmin)
