from django_filters import rest_framework as django_filters

from .models import Book

class BookFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__last_name', lookup_expr='icontains')
    genre = django_filters.CharFilter(field_name='genre__name', lookup_expr='icontains')
    published_date = django_filters.DateFilter(field_name='published_date', lookup_expr='exact')

    class Meta:
        model = Book
        fields = ['author', 'genre', 'published_date']