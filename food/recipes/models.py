from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from recipes.validators import hex_color_validator, ingrent_validator
from users.constants import (MAX_USER,
                             MAX_RECIPES,
                             MAX_UNIT,
                             NAME_TEG,
                             COLOR_TEG,
                             SLUG,
                             MAX,
                             MIN,)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингредиент',
                            validators=[ingrent_validator],
                            max_length=MAX_USER, unique=True,)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=MAX_UNIT,)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='Название тега',
                            max_length=NAME_TEG, unique=True)
    color = models.CharField(verbose_name='Цвет тега', max_length=COLOR_TEG,
                             validators=[hex_color_validator], unique=True)
    slug = models.SlugField(verbose_name='Слаг', max_length=SLUG, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        unique_together = ('name', 'color', 'slug')

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Рецепт', max_length=MAX_RECIPES, blank=False,)
    image = models.ImageField('Картинка',
                              upload_to='recipe_images/',
                              blank=False)
    text = models.TextField(verbose_name='Описание',
                            blank=False)
    tags = models.ManyToManyField(Tag, verbose_name='Теги',
                                  related_name='tags', db_index=True,)
    cooking_time = models.PositiveSmallIntegerField('Время приготовления',
                                                    blank=False,
                                                    validators=[
                                                        MaxValueValidator(MAX),
                                                        MinValueValidator(MIN),
                                                    ],)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,)
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,)
    amount = models.PositiveIntegerField('Количество ингредиента')

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиента'
        contraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_ingredient_in_recipe',
            ),
        )

    def __str__(self):
        return f'{self.ingredients}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="user_favorite")
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_favorite")

    class Meta:
        ordering = ("user",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_name_favorite_recipe"
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping_list"
    )
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_list",
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Корзина"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_name_shopping_list_recipe"
            )
        ]
