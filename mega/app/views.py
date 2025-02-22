from django.contrib.auth import get_user_model
from django_filters import rest_framework as django_filters
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from datetime import timedelta

from rest_framework.filters import OrderingFilter
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from .forms import AuthorForm, BookForm, GenreForm

from .filters import BookFilter
from .models import Author, Book, FavoriteBook, Genre
from .serializers import (AuthorSerializer, BookSerializer, 
                          FavoriteBookSerializer, GenreSerializer, 
                          LoginSerializer, RegisterSerializer)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer



class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter, OrderingFilter)
    filterset_class = BookFilter
    search_fields = ['title', 'author__last_name']
    ordering_fields = ['publication_date', 'author__first_name', 'genre__name']
    ordering = ['publication_date'] 

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class FavoriteBookViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteBookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteBook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        favorites = FavoriteBook.objects.filter(user=request.user)
        deleted_count, _ = favorites.delete()
        if deleted_count == 0:
            return Response({"message": "Нет книг для удаления из избранного."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": f"Удалено {deleted_count} книг из избранного."}, status=status.HTTP_204_NO_CONTENT)
    

class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Неверные учетные данные'})
        

class IndexPageView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()

        yesterday = today - timedelta(days=1)
        new_books = Book.objects.filter(publication_date__gte=yesterday)

        anniversary_years = [5, 10, 20, 50, 100]
        anniversary_books = Book.objects.filter(publication_date__year__in=[
            today.year - year for year in anniversary_years
        ])
        context['today'] = today

        context['new_books'] = new_books
        context['anniversary_books'] = anniversary_books

        context['has_new_books'] = new_books.exists()
        context['has_anniversary_books'] = anniversary_books.exists()

        return context




class LogoutView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login') 




class RegistrationPageView(View):
    def get(self, request):
        return render(request, 'registration.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует.")
            return render(request, 'registration.html')

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        login(request, user)

        messages.success(request, "Вы успешно зарегистрированы!")
        return redirect('index')


# ---------------------------------------------------------



class BookCreateView(SuccessMessageMixin,CreateView):
    model = Book
    form_class = BookForm
    template_name = 'book_create.html'
    success_url = reverse_lazy('book_list')
    success_message = "Книга успешно добавлена!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['genres'] = Genre.objects.all()
        return context
    
    def form_valid(self, form):
        return super().form_valid(form)

class AuthorCreateView(SuccessMessageMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'author_create.html'
    success_url = reverse_lazy('author_list') 
    success_message = "Автор успешно добавлен!"

    def form_valid(self, form):
        return super().form_valid(form)

class GenreCreateView(SuccessMessageMixin, CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'genre_create.html'
    success_url = reverse_lazy('genre_list')
    success_message = "Жанр успешно добавлен!"

    def form_valid(self, form):
        return super().form_valid(form)


# ------------------------------------------------------------

class BookDeleteView(SuccessMessageMixin, DeleteView):
    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    success_message = "Книга успешно удалена!"

class AuthorDeleteView(SuccessMessageMixin, DeleteView):
    model = Author
    template_name = 'author_confirm_delete.html'
    success_url = reverse_lazy('author_list')
    success_message = "Автор успешно удален!"

class GenreDeleteView(SuccessMessageMixin, DeleteView):
    model = Genre
    template_name = 'genre_confirm_delete.html'
    success_url = reverse_lazy('genre_list')
    success_message = "Жанр успешно удален!"


# ------------------------------------------------------------- 


class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_books = FavoriteBook.objects.filter(user=self.request.user).values_list('book_id', flat=True)
        context['favorite_books'] = favorite_books
        return context

class AuthorListView(ListView):
    model = Author
    template_name = 'author_list.html'
    context_object_name = 'authors'

class GenreListView(ListView):
    model = Genre
    template_name = 'genre_list.html'
    context_object_name = 'genres'
    
# ------------------------------------------------------------


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'author_detail.html'
    context_object_name = 'author'

# ------------------------------------------------------------


class BookUpdateView(SuccessMessageMixin, UpdateView):
    model = Book
    template_name = 'book_update.html'
    fields = ['title', 'summary', 'isbn', 'publication_date']
    success_message = "Книга успешно обновлена!"

    def form_valid(self, form):
        authors = self.request.POST.getlist('authors')
        genres = self.request.POST.getlist('genres')
        book = form.save(commit=False)
        book.save()
        book.author.set(authors)  # Устанавливаем авторов
        book.genre.set(genres)    # Устанавливаем жанры
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['genres'] = Genre.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})
    

class AuthorUpdateView(SuccessMessageMixin, UpdateView):
    model = Author
    template_name = 'author_update.html'
    context_object_name = 'author'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    success_message = "Автор успешно обновлен!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('author_detail', kwargs={'pk': self.object.pk})
    

# ---------------------------------------------------------------------------

class AddToFavoritesView(View):
    def post(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        favorite, created = FavoriteBook.objects.get_or_create(user=request.user, book=book)

        if created:
            messages.success(request, f'Книга "{book.title}" добавлена в избранное!')
        else:
            messages.warning(request, f'Книга "{book.title}" уже есть в избранном!')

        return redirect('book_list')
    

class FavoriteBookListView(ListView):
    model = FavoriteBook
    template_name = 'favorite_books.html'
    context_object_name = 'favorite_books'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).select_related('book')
    

class RemoveFromFavoritesView(View):
    def post(self, request, favorite_id):
        favorite = get_object_or_404(FavoriteBook, id=favorite_id, user=request.user)
        favorite.delete()
        messages.success(request, "Книга была удалена из избранных.")
        return redirect('favorite_books')