from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import( UserViewSet, IngredientViewSet,
                   RecipesViewSet, TagViewSet)

app_name = 'api'
router = DefaultRouter

router.register('users', UserViewSet, basename='user')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
