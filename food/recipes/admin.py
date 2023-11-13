from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipes,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    fields = ('author', 'name', 'added_to_favorite')
    list_display = ('id', 'author', 'name', 'added_to_favorite')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientLine)

    def added_to_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(RecipeIngredient)
class RecipeInredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe', 'ingredient')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name', 'color')
    search_fields = ('name', 'color')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
