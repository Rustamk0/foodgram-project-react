from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from django.db.models import Sum
from django.http import HttpResponse

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_fremework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from recipes.models import (Favorite, Ingredient, Recipes, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User
from .filter import IngredientFilter, RecipeFilters
from .pagination import PagePagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (UserSerializer, FavoriteSerializer,
                          ShoppingCartSerializer, FollowCreateSerializer,
                          FollowReadSerializer, IngredientSerializer,
                          RecipesReadSerializer, RecipesCreateUpdateSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ModelViewset):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get,')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesCreateUpdateSerializer
    permission_class = (IsOwnerOrReadOnly,)
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return RecipesReadSerializer
        return self.serializer_class

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk=None):
        recipe_to_favorite = get_object_or_404(Recipes, id=pk)
        user = self.request.user
        if self.request.method == 'DELETE':
            get_object_or_404(
                Favorite,
                user=user,
                recipe=recipe_to_favorite
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        favorite_data = {'user': user.id, 'recipe': recipe_to_favorite.id}
        favorite_serializer = FavoriteSerializer(data=favorite_data)
        favorite_serializer.is_valid(raise_exception=True)
        favorite_serializer.save()
        return Response(
            favorite_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk=None):
        recipe_to_favorite = get_object_or_404(Recipes, id=pk)
        user = self.request.user
        if self.request.method == 'DELETE':
            get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe_to_favorite
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        favorite_data = {'user': user.id, 'recipe': recipe_to_favorite.id}
        favorite_serializer = ShoppingCartSerializer(data=favorite_data)
        favorite_serializer.is_valid(raise_exception=True)
        favorite_serializer.save()
        return Response(
            favorite_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        ingredient_list = RecipeIngredient.objects.filter(
            recipe__shopping_lists_recipe__user=request.user
        ).order_by('ingredient__name')
        ingredient_totals = ingredient_list.values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                total_amount=Sum('amount'))

        text = ''
        for ingredient in ingredient_totals:
            text += (
                f'{ingredient["ingredient__name"]}, '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename=your_shopping_cart.txt')
        return response


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = PagePagination

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(["get"], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=PagePagination
    )
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = User.objects.filter(followers__user=user)
        subscriptions = self.paginate_queryset(subscriptions)
        serializer = FollowReadSerializer(
            data=subscriptions,
            many=True,
            context={'request': request}
        )
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, id=None):
        user_to_follow = get_object_or_404(User, id=id)
        user = self.request.user
        if self.request.method == 'DELETE':
            get_object_or_404(
                Follow,
                user=user,
                author=user_to_follow
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        follow_data = {'user': user.id, 'author': user_to_follow.id}
        follow_serializer = FollowCreateSerializer(
            data=follow_data,
            context={'request': request}
        )
        follow_serializer.is_valid(raise_exception=True)
        follow_serializer.save()
        return Response(follow_serializer.data, status=status.HTTP_201_CREATED)
