from core.fields import Base64ImageField
from django.db.models import F
from recipes.models import Ingredient, IngredientAmount, Recipe
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from tags.serializers import TagSerializer
from users.serializers import UserSerializer


class RecipeSerializer(ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'name',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'image', 'text', 'cooking_time', ]

    @staticmethod
    def get_ingredients(obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F(
                'ingredientamount__amount')
        )

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

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise ValidationError('Ингридиенты должны '
                                      'быть уникальными')
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
        tags_data = self.initial_data.get('tags')
        recipe = Recipe.objects.create(
            image=image,
            author=request.user,
            **validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_instance = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id'))
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient_instance,
                amount=amount)

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
