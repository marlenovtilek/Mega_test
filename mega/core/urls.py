from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

from app.views import (AddToFavoritesView, AuthorCreateView, AuthorDeleteView, AuthorDetailView, AuthorListView, 
                       AuthorUpdateView, BookCreateView, BookDeleteView, BookDetailView, BookListView, BookUpdateView, 
                       FavoriteBookListView, GenreCreateView, GenreDeleteView, GenreListView, IndexPageView, LoginPageView, 
                       LogoutView, RegistrationPageView, RemoveFromFavoritesView,
                       )

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Документация API с помощью Swagger",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('', LoginPageView.as_view(), name='login'),
    path('index/', IndexPageView.as_view(), name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegistrationPageView.as_view(), name='register'),

    path('books/', BookListView.as_view(), name='book_list'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('genres/', GenreListView.as_view(), name='genre_list'),

    path('create_book/', BookCreateView.as_view(), name='book_create'),
    path('create_author/', AuthorCreateView.as_view(), name='author_create'),
    path('create_genre/', GenreCreateView.as_view(), name='genre_create'),

    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('author/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),

    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('authors/<int:pk>/delete/', AuthorDeleteView.as_view(), name='author_delete'),
    path('genres/<int:pk>/delete/', GenreDeleteView.as_view(), name='genre_delete'),

    path('books/<int:pk>/edit/', BookUpdateView.as_view(), name='book_update'),
    path('authors/<int:pk>/edit/', AuthorUpdateView.as_view(), name='author_update'),

    path('books/<int:pk>/add_to_favorites/', AddToFavoritesView.as_view(), name='add_to_favorites'),
    path('favoritebooks/', FavoriteBookListView.as_view(), name='favorite_books'),
    path('favorites/remove/<int:favorite_id>/', RemoveFromFavoritesView.as_view(), name='remove_from_favorites'),

    


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
