from django.db.models import F, Sum
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.filters import IngredientsFilter, RecipesFilter
from recipes.models import Ingredient, IngredientAmount, Recipe
from recipes.permissions import AuthorOrReadOnly
from recipes.serializers import IngredientSerializer, RecipeSerializer
from users.serializers import ShortRecipeSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly, )
    filter_class = RecipesFilter

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
        cart_list = {}
        user = request.user
        # TODO - Кол-во можно сразу посчитать в запросе при помощи annotate
        # ingredients = IngredientAmount.objects.filter(
        #     recipe__cart__user=request.user).values_list(
        #     'ingredient__name', 'ingredient__measurement_unit'
        # ).annotate(amount=Sum('amount'))
        # for item in ingredients:
        #     name = item[0]
        #     if name not in cart_list:
        #         cart_list[name] = {
        #             'measurement_unit': item[1],
        #             'amount': item[2]
        #         }
        #     else:
        #         cart_list[name]['amount'] += item[2]
        # -----------------------------------------------------------------
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user).order_by(
            'ingredient__name').values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(amount_total=Sum('amount'))

        # # DEBUG --------------------------------------------------------------
        # import pdb
        # pdb.set_trace()
        # # DEBUG --------------------------------------------------------------

        cart_list = ''
        for item in ingredients:
            cart_list += (
                f'{item["amount_total"]}'
                f' {item["ingredient__measurement_unit"]}\n'
            )
        # ----------------------------------------------------------------

        pdfmetrics.registerFont(TTFont('JetBrainsMono-Regular',
                                       'JetBrainsMono-Regular.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.pdf"')
        p = canvas.Canvas(response)
        p.setFont('JetBrainsMono-Regular', size=10)
        # p.drawString(70, 770, 'Список покупок')
        p.drawString(70, 770, cart_list)
        p.setFont('JetBrainsMono-Regular', size=16)
        height = 730
        # for name, data in cart_list.items():
        #     p.drawString(
        #         90,
        #         height,
        #         f'{name} ({data["measurement_unit"]}) — {data["amount"]}')
        #     height -= 25
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
