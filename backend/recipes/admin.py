from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.safestring import mark_safe

from .models import Cart, Favorite, Ingredient, IngredientAmount, Recipe


class IngredientInline(TabularInline):
    model = IngredientAmount
    extra = 1


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
    )
    list_display_links = ('name', )
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name', 'text', )
    empty_value_display = '-пусто-'
    readonly_fields = ('count_favorites', 'preview', )
    inlines = (IngredientInline, )
    save_on_top = True
    actions_on_bottom = True
    fields = (
        ('name', 'author'),
        'text', 'image', 'preview', 'cooking_time', 'tags', 'count_favorites',
    )

    def count_favorites(self, obj):
        return obj.favorites.count()
    count_favorites.short_description = 'В избранном'

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" '
                         f'style="max-height: 200px;">')

    preview.short_description = 'Предпросмотр'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_display_links = ('name', )
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    list_display_links = ('recipe', )
    search_fields = ('recipe', 'ingredient', )
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_display_links = ('user', )
    search_fields = ('recipe', 'user', )
    empty_value_display = '-пусто-'


class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_display_links = ('user', )
    search_fields = ('recipe', 'user', )
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Cart, CartAdmin)
