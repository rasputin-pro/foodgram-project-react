from rest_framework.exceptions import ValidationError
from rest_framework.fields import (IntegerField, ListField, ReadOnlyField,
                                   SerializerMethodField)
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from core.fields import Base64ImageField
from recipes.models import Ingredient, IngredientAmount, Recipe
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import UserSerializer


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountReadSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountCreateSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    @staticmethod
    def get_ingredients(obj):
        recipe = obj
        queryset = recipe.recipe_ingredient.all()
        return IngredientAmountReadSerializer(queryset, many=True).data

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj.id).exists()


class RecipeCreateSerializer(ModelSerializer):
    image = Base64ImageField()
    tags = ListField(
        child=SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )
    ingredients = IngredientAmountCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time', ]

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хоть один ингредиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise ValidationError('Ингредиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            image=image,
            author=request.user,
            **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient_amount(ingredients, recipe)
        return recipe

    @staticmethod
    def create_ingredient_amount(ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_ingredient_amount(
            validated_data.pop('ingredients'),
            instance
        )
        return super(RecipeCreateSerializer, self).update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
