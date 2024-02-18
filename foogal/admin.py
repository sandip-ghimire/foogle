from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import Setting, File, Link, Config, Attribute

admin.site.register(Config)
admin.site.register(Attribute)


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']


admin.site.register(Session, SessionAdmin)


class FileInline(admin.TabularInline):
    model = File
    extra = 0


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    inlines = [FileInline, LinkInline]


admin.site.register(File)
admin.site.register(Link)
