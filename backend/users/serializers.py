from core.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (CharField, ReadOnlyField,
                                   SerializerMethodField)
from rest_framework.serializers import ModelSerializer, Serializer
from users.models import Follow, User


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'password', 'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class SetPasswordSerializer(Serializer):
    current_password = CharField(
        max_length=128,
        write_only=True,
        required=True
    )
    new_password = CharField(
        max_length=128,
        write_only=True,
        required=True
    )

    def validate_current_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise ValidationError(
                'Текущий пароль введён неверно!'
            )
        return value

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['user']
        user.set_password(password)
        user.save()
        return user


class FollowSerializer(ModelSerializer):
    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    @staticmethod
    def get_is_subscribed(obj):
        return obj.user.follower.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.author.recipes.all().count()


class ShortRecipeSerializer(ModelSerializer):
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
