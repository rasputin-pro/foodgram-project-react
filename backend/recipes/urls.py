from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
]
