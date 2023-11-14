from drf_extra_fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserSerializer

from users.models import Follow, User
from recipes.models import (Favorite,
                            Ingredient,
                            Recipes,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag,)

from food.settings import MIN_VAL_NUM, MAX_VAL_NUM


class UserSerializer(UserSerializer):
    is_subcribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subcribed',
        ]
        read_only_fields = ['is_subscribed']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.IntegerField(source='ingredient.name')
    measurement_unit = serializers.IntegerField(
      source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='ingredient'
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.cart.filter(user=user).exists


class RecipesM2MSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(
        min_value=MIN_VAL_NUM, max_value=MAX_VAL_NUM, error_message={
            'min_value': 'Мин. значение не менее 1.',
            'max_value': 'Макс. значение не менее 32000.'
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipesCreateUpdateSerializer(serializers.ModelSerializer):
    ingredient = RecipesM2MSerializer(many=True,
                                      source='ingredient')
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VAL_NUM, max_value=MAX_VAL_NUM, error_message={
            'min_value': 'Мин. значение не менее 1.',
            'max_value': 'Макс. значение не менее 32000.'
        }
    )

    class Meta:
        model = Recipes
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cookeng_time',
        )

    def empty_field(self, field, value):
        if field := value:
            return field
        else:
            raise ValidationError({
                f"{field}": "Выберите что-нибудь!"
            })

    def validate_ingredients(self, value):
        ingredients = self.empty_field('ingredients', value)
        if not ingredients:
            raise ValidationError({
                "ingredients": "Добавьте хотя бы один ингредиент!"
            })
        ingredients_in_recipe = []
        for ingredient in ingredients:
            if ingredient in ingredients_in_recipe:
                raise ValidationError({
                    "ingredients": "Вы уже добавили этот ингредиент!"
                })
            ingredients_in_recipe.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = self.empty_field(
        )
        if not tags:
            raise ValidationError({
                "tags": "Добавьте хотя бы один тег!"
            })
        tags_in_recipe = []
        for tag in tags:
            if tag in tags_in_recipe:
                raise ValidationError({
                    "tags": "Этот тег уже выбран!"
                })
            tags_in_recipe.append(tag)
        return value


class RecipeFollowSerializer(serializers.ModelSerializer):
    image = Base64ImageField

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowReadSerializer(serializers.ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subcribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, objects):
        return objects.recipes.count()

    def get_recipes(self, objects):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        recipes = objects.recipes.all()[:int(
            recipes_limit)] if recipes_limit else objects.recipes.all()
        return RecipeFollowSerializer(recipes, many=True, read_only=True).data

    def get_is_subscribed(self, objects):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and user.follower.filter(author=objects).exists()
        )


class FollowCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
        )

    def validate(self, attrs):
        user = attrs.get('user')
        author = attrs.get('author')
        if user == author:
            raise serializers.ValidationEror('Нельзя подписаться на себя')
        if user in author.followers.all():
            raise ValidationError('Вы уже подписаны на автора')
        return super().validate(attrs)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowReadSerializer(instance.author, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializers):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']

        if user.shopping_list_user.filter(recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Рецепт в списке покупок'}
            )
        return super().validate(attrs)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeFollowSerializer(instance.recipes, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if user.favorites.filter(recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Рецепт в избраном'})
        return super().validate(attrs)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'reauest': request}
        return RecipeFollowSerializer(instance.recipes, context=context).data
