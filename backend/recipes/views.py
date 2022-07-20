from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.filters import IngredientsFilter, RecipesFilter
from recipes.models import Ingredient, IngredientAmount, Recipe
from recipes.permissions import AuthorOrReadOnly
from recipes.serializers import (IngredientSerializer, RecipeCreateSerializer,
                                 RecipeReadSerializer)
from users.serializers import ShortRecipeSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly, )
    filter_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, ))
    def favorite(self, request, pk=None):
        related = request.user.favorites
        obj = related.filter(recipe=pk)
        if request.method == 'POST':
            return self.add_object(related, obj, pk)
        elif request.method == 'DELETE':
            return self.delete_object(obj)
        return None

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        related = request.user.cart
        obj = related.filter(recipe=pk)
        if request.method == 'POST':
            return self.add_object(related, obj, pk)
        elif request.method == 'DELETE':
            return self.delete_object(obj)
        return None

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user).order_by(
            'ingredient__name').values(
                'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount_total=Sum('amount'))

        pdfmetrics.registerFont(TTFont('JetBrainsMono-Regular',
                                       'JetBrainsMono-Regular.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.pdf"')

        p = canvas.Canvas(response)
        per = 28
        for g in range(0, len(ingredients), per):
            page_num = p.getPageNumber()
            p.setFont('JetBrainsMono-Regular', size=21)
            p.drawString(90, 770, f'Список покупок, стр. {page_num}')
            p.setFont('JetBrainsMono-Regular', size=16)
            height = 730
            for i in range(g, g + per):
                if i >= len(ingredients):
                    continue
                p.drawString(
                    90, height,
                    f'{ingredients[i]["ingredient__name"]} '
                    f'({ingredients[i]["ingredient__measurement_unit"]}) —'
                    f' {ingredients[i]["amount_total"]}')
                height -= 25
            p.showPage()
        p.save()
        return response

    @staticmethod
    def add_object(related, obj, pk):
        if obj.exists():
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                status=HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        related.create(recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @staticmethod
    def delete_object(obj):
        if obj.exists():
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удалён.'
        }, status=HTTP_400_BAD_REQUEST)


class IngredientViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny, )
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsFilter, )
    search_fields = ('^name', )
    pagination_class = None
