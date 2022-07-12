from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializers import (FollowSerializer, SetPasswordSerializer,
                               UserSerializer)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request):
        user = request.user
        serializer = SetPasswordSerializer(
            user,
            data=request.data,
            context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        follow = user.follower.filter(author=author)
        if request.method == 'DELETE':
            if user == author:
                return Response(
                    {'errors': 'Вы не можете отписываться от самого себя'},
                    status=HTTP_400_BAD_REQUEST
                )
            if follow.exists():
                follow.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы уже отписались'},
                status=HTTP_400_BAD_REQUEST
            )

        if user == author:
            return Response(
                {'errors': 'Вы не можете подписываться на самого себя'},
                status=HTTP_400_BAD_REQUEST
            )
        if follow.exists():
            return Response(
                {'errors': 'Вы уже подписаны на данного пользователя'},
                status=HTTP_400_BAD_REQUEST
            )
        follow = user.follower.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=HTTP_201_CREATED)
