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
    permission_class = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return RecipesCreateUpdateSerializer
        return RecipesReadSerializer

    def shopping_or_favorite(self, current_model, current_serializer, request,
                             pk=None):
        user = request.user.id
        if not Recipes.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            basket = current_model.objects.filter(user=user, recipe=pk)
            if basket.exists():
                basket.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipes.objects.get(id=pk)
        serializer = current_serializer(
            data={
                "user": user,
                "recipe": pk,
                "name": recipe.name,
                "image": recipe.image,
                "cooking_time": recipe.cooking_time,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
            methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.shopping_or_favorite(Favorite,
                                         FavoriteSerializer, pk=pk)

    @action(
            methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,)
    )
    def shopping_card(self, request, pk=None):
        return self.shopping_or_favorite(ShoppingCart,
                                         ShoppingCartSerializer, pk=pk)

    @action(
            methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredient_list = RecipeIngredient.objects.filter(
            recipe__shopping_lists_recipe__user=request.user).order_by(
                'ingredient__name')
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


class SubUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = PagePagination

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
