from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name',
                       'last_name',)
    email = models.EmailField(
        'email',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=150,
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
        ]
        ordering = ('id',)
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
