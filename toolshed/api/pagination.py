from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    """Bump the pagination size up significantly.

    This tends to get used in inverse proportion to the size/query time for a
    particular view. I.e. tags which are tiny and require only a simple join
    query for finding number_of_repos, can have a much higher pagination level
    to facilitate easy display
    """
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000
