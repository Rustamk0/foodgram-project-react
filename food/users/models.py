from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (MAX_EMAIL, MAX_USER, MAX_NAME, MAX_LAST_NAME)
from recipes.validators import uni_validator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name',
                       'last_name',)
    email = models.EmailField(
        'email',
        max_length=MAX_EMAIL,
        unique=True,
    )
    username = models.CharField(
        max_length=MAX_USER,
        unique=True,
        validators=([uni_validator],)
    )
    first_name = models.CharField(
        max_length=MAX_NAME,
        blank=False,
        null=False,
        validators=[uni_validator],
    )
    last_name = models.CharField(
        max_length=MAX_LAST_NAME,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),

            models.CheckConstraint(
                name="%(app_label)s_%(class)s_prevent_self_follow",
                check=~models.Q(follower=models.F("author")),)
        ]
        ordering = ('author',)
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
