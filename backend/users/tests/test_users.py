import pytest


class TestUserAPI:

    @pytest.mark.django_db(transaction=True)
    def test_user_registration(self, client):
        response = client.post(
            '/api/users/',
            data={
                'username': 'TestUser2',
                'password': 'PaSSWoRD2',
                'email': 'test_user2@mail.ru',
                'first_name': 'First',
                'last_name': 'Last',
            }
        )
        assert response.status_code != 404, (
            'Страница `/api/users/` не найдена'
        )
        assert response.status_code == 201, (
            'Страница `/api/users/` работает не правильно'
        )
        auth_data = response.json()
        verified_data = ['username', 'email', 'first_name', 'last_name', 'id']
        for field in verified_data:
            assert field in auth_data, (
                'Проверьте, что при POST запросе `/api/users/` возвращаете '
                f'{field}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_token_getting(self, client, user):

        response = client.post(
            '/api/auth/token/login/',
            data={'email': 'test_user1@mail.ru', 'password': 'PaSSWoRD1'}
        )
        assert response.status_code != 404, (
            'Страница `/api/auth/token/login/` не найдена'
        )
        assert response.status_code == 200, (
            'Страница `/api/auth/token/login/` работает не правильно'
        )
        auth_data = response.json()
        assert 'auth_token' in auth_data, (
            'Проверьте получение токена, при POST запросе '
            '`/api/auth/token/login/`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_api_endpoints_for_user(self, user_client, client):
        endpoints = [
            '/api/users/me/',
            '/api/users/subscriptions/',
            '/api/users/set_password/',
            '/api/auth/token/logout/',
        ]
        for endpoint in endpoints:
            response = user_client.get(endpoint)
            assert response.status_code != 404, (
                f'Страница {endpoint} не найдена'
            )
            response = client.get(endpoint)
            assert response.status_code == 401, (
                f'Страница {endpoint} должна быть закрыта для гостя'
            )

    @pytest.mark.django_db(transaction=True)
    def test_api_endpoints_for_guest(self, client, user):
        endpoints = [
            '/api/users/',
            f'/api/users/{user.id}/',
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code != 404, (
                f'Страница {endpoint} не найдена'
            )
            assert response.status_code != 401, (
                f'Страница {endpoint} должна быть открыта для гостя'
            )
            assert response.status_code == 200, (
                f'Страница {endpoint} работает не правильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_user_set_password(self, user_client):
        response = user_client.post(
            '/api/users/set_password/',
            data={'current_password': 'WrongPassword',
                  'new_password': 'PaSSWoRD11'}
        )
        assert response.status_code == 400, (
            'Неверный код ошибки при передаче некорректных данных!'
        )
        response = user_client.post(
            '/api/users/set_password/',
            data={'current_password': 'PaSSWoRD1',
                  'new_password': 'PaSSWoRD11'}
        )
        assert response.status_code == 204, (
            'Смена пароля не работает'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_to_user(self, user_client, another_user):
        response = user_client.post(
            f'/api/users/{another_user.id}/subscribe/',
            data=None
        )
        assert response.status_code == 201, (
            'Подписка на автора не работает!'
        )
        response = user_client.delete(
            f'/api/users/{another_user.id}/subscribe/',
            data=None
        )
        assert response.status_code == 204, (
            'Отписка от автора не работает!'
        )

    @pytest.mark.django_db(transaction=True)
    def test_delete_token(self, user_client):
        response = user_client.post(
            '/api/auth/token/logout/',
            data=None
        )
        assert response.status_code == 204, (
            'Удаление токена не работает!'
        )
