from django_filters.rest_framework import FilterSet, filters

from rest_framework.filters import SearchFilter
from recipes.models import Recipes


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    author = filter.ModelChoiceFilter(field_name="author__id")
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

        def is_favorite(self, queryset, name, value):
            user = self.request.user
            if value and user.is_authenticated:
                return queryset.filter(recipe_favorite__user=user)
            return queryset

        def shopping_cart(self, queryset, name, value):
            user = self.request.user
            if value and user.is_authenticated:
                return queryset.filter(shopping_list__user=user)
            return queryset
