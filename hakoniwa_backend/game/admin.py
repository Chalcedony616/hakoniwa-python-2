from django.contrib import admin
from .models import GlobalSettings, Island, IslandBackup, MapTile, Plan, Log, History

admin.site.register(GlobalSettings)
admin.site.register(Island)
admin.site.register(IslandBackup)
admin.site.register(MapTile)
admin.site.register(Plan)
admin.site.register(Log)
admin.site.register(History)