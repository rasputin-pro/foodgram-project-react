from django.contrib import admin

from .models import Tag


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug', )
    list_display_links = ('name', )
    list_editable = ('color', )
    search_fields = ('name', 'slug', 'color', )
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagsAdmin)
