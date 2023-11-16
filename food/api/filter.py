from django_filters.rest_framework import FilterSet, filters

from rest_framework.filters import SearchFilter
from recipes.models import Ingredient, Recipes
from users.models import User

class IngredientFilter(SearchFilter):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
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

        def filter_is_favorited(self, queryset, name, value):
            if value and self.request.user.is_authenticated:
                return queryset.filter(favorites__user=self.request.user)
            return queryset

        def filer_is_in_shopping_cart(self, queryset, name, value):
            if value and self.request.user.is_authenticated:
                return queryset.filter(shopping_cart__user=self.request.user)
            return queryset


class AuthorFilter(FilterSet):
    
    username = filters.CharFilter(lookup_expr='startswith')
    email = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = User
        fields = {
            'username',
            'email',
        }