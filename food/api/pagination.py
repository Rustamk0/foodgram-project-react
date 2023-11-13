from rest_framework.pagination import PageNumberPagination
from food.settings import PAG_LIMIT, PAG_MAX_LIMIT

class PagePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAG_LIMIT
    limit = PAG_LIMIT
    max_page_limit = PAG_MAX_LIMIT
