from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Пользовательская пагинация.
    Ограничения количества объектов - по атрибуту: limit.
    Выбор страницы - по атрибуту: page.
    """
    page_size_query_param = 'limit'
