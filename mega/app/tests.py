import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import date
from django.contrib.messages import get_messages

from django.core import mail
from django.utils import timezone
from datetime import timedelta
from .tasks import send_daily_new_books, send_anniversary_books


from django.test import Client, TestCase
from app.models import Author, Book, CustomUser, FavoriteBook, Genre

User = get_user_model()

class RegisterViewTests(APITestCase):

    def test_register_user_success(self):
        url = '/api/v1/register/' 
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'test@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_register_user_existing_username(self):
        User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        url = '/api/v1/register/' 
        data = {
            'username': 'testuser',
            'password': 'testpassword2',
            'email': 'test2@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)


class LoginViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_user_success(self):
        url = '/api/v1/login/'
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data) 
        self.assertIn('refresh', response.data)

    def test_login_user_invalid_credentials(self):
        url = '/api/v1/login/' 
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class AuthorViewSetTests(APITestCase):

    def setUp(self):
        self.author = Author.objects.create(first_name='Author One')

    def test_author_list(self):
        url = '/api/v1/authors/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_author_create(self):
        url = '/api/v1/authors/'
        data = {
            'first_name': 'New',           
            'last_name': 'Author',           
            'biography': 'This is a new author biography.', 
            'date_of_birth': '1990-01-01',     
            'date_of_death': '',          
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)


class BookViewSetTests(APITestCase):

    def setUp(self):
        self.author = Author.objects.create(first_name='Author', last_name='One')
        self.genre = Genre.objects.create(name='Fiction')
        self.book = Book.objects.create(
            title='Test Book',
            publication_date='2023-01-01',
            isbn=1234567890
        )
        self.book.author.add(self.author)

    def test_book_list(self):
        url = '/api/v1/books/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_book_create(self):
        url = '/api/v1/books/'
        data = {
            'title': 'New Book',
            'summary': 'This is a new book.',
            'isbn': 9876543210, 
            'author': [self.author.id],
            'publication_date': '2023-01-01',
            'genre': [1],
        }
        response = self.client.post(url, data)


        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)


class GenreViewSetTests(APITestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name='Fiction')

    def test_genre_list(self):
        url = '/api/v1/genres/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_genre_create(self):
        url = '/api/v1/genres/'
        data = {'name': 'Non-Fiction'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 2)


class FavoriteBookViewSetTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser', password='testpassword')
        self.author = Author.objects.create(first_name='Author', last_name='Last Name', biography='Biography')
        self.book = Book.objects.create(title='Test Book', summary='This is a test book.', isbn=1234567890, publication_date='2023-01-01')
        self.favorite_book = FavoriteBook.objects.create(user=self.user, book=self.book) 

    def test_favorite_book_list(self):
        url = '/api/v1/favorites/'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_clear_favorites(self):
        url = '/api/v1/favorites/clear/'
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title='Test Book',
            publication_date=date.today(),
            isbn='123456789'
        )
        self.book.author.set([self.author])


        FavoriteBook.objects.create(user=self.user, book=self.book)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FavoriteBook.objects.count(), 0)


# ----------------------------------------------------------------------------------------------




class LoginPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass'
        self.url = reverse('login')
        User.objects.filter(email='test@example.com').delete()
        self.user = User.objects.create_user(username=self.username, email='test@example.com', password=self.password)

    def test_get_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.url, {'username': self.username, 'password': 'testpass'})
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.url, {'username': 'invaliduser', 'password': 'invalidpass'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Неверные учетные данные')



class IndexPageViewTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'password'
        self.user = User.objects.create_user(username=self.username, email='test@example.com', password=self.password)

    def test_get_index_page(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class LogoutViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = f'testuser_{uuid.uuid4()}'
        cls.user = User.objects.create_user(username=cls.username, email='test@example.com', password='testpass')
        cls.url = reverse('logout')

    def test_logout(self):
        self.client.login(username=self.username, password='testpass')
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RegistrationPageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('register')

    def test_get_registration_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')

    def test_registration_with_valid_data(self):
        username = f'newuser_{uuid.uuid4()}' 
        
        response = self.client.post(self.url, {
            'username': username,
            'email': 'newuser@example.com',
            'password': 'newpassword'
        })

        self.assertRedirects(response, reverse('index'))


        self.assertTrue(User.objects.filter(username=username).exists())


        user = User.objects.get(username=username)
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)


    def test_registration_with_existing_username(self):
        User.objects.create_user(username='existinguser', email='test@example.com', password='password')

        response = self.client.post(self.url, {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)


        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Пользователь с таким именем уже существует." in str(m) for m in messages))


# ---------------------------------------------------------------------------------------------------

class BookCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse('book_create')
        self.genre = Genre.objects.create(name='Жанр') 
        self.author = Author.objects.create(first_name='Тест', last_name='Автор', biography='Тестовая биография')

    def test_book_create_view_get(self):
        """Проверка, что страница создания книги открывается"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('authors', response.context)
        self.assertIn('genres', response.context)

    def test_book_create_view_post(self):
        response = self.client.post(self.url, {
            'title': 'Новая Книга',
            'summary': 'Краткое содержание новой книги',
            'isbn': 1234567890,
            'author': [self.author.id], 
            'publication_date': '2023-01-01',
            'genre': [self.genre.id],  
        })
        self.assertTrue(Book.objects.filter(title='Новая Книга').exists())
        self.assertEqual(response.status_code, 302)
        


class AuthorCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse('author_create')

    def test_author_create_view_get(self):
        """Проверка, что страница создания автора открывается"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_author_create_view_post(self):
        response = self.client.post(self.url, {
            'first_name': 'Новый',
            'last_name': 'Автор',
            'biography': 'Биография нового автора',
            'date_of_birth': '1990-01-01',
        })
        
        self.assertTrue(Author.objects.filter(first_name='Новый', last_name='Автор').exists())
        self.assertEqual(response.status_code, 302)  


class GenreCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('genre_create')

    def test_genre_create_view_get(self):
        """Проверка, что страница создания жанра открывается"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_genre_create_view_post(self):
        """Проверка, что жанр создается"""
        response = self.client.post(self.url, {'name': 'Новый Жанр'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Genre.objects.filter(name='Новый Жанр').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Жанр успешно добавлен!", [msg.message for msg in messages])



class BookDeleteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass') 
        self.client.login(username='testuser', password='testpass')  
        self.book = Book.objects.create(
            title='Книга для удаления',
            isbn=123456789,
            publication_date='2025-01-01'
        )
        self.url = reverse('book_delete', args=[self.book.pk])  

    def test_book_delete_view(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('book_list'))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists()) 


class AuthorDeleteViewTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name='Автор для удаления',
            last_name='Тестовый',
            biography='Биография тестового автора'
        )
        self.url = reverse('author_delete', args=[self.author.pk])  

    def test_author_delete_view(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('author_list'))
        self.assertFalse(Author.objects.filter(pk=self.author.pk).exists()) 


class GenreDeleteViewTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(
            name='Жанр для удаления'
        )
        self.url = reverse('genre_delete', args=[self.genre.pk])  

    def test_genre_delete_view(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('genre_list'))
        self.assertFalse(Genre.objects.filter(pk=self.genre.pk).exists())



class BookListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.genre = Genre.objects.create(name='Тестовый Жанр')
        self.book = Book.objects.create(
            title='Тестовая Книга',
            isbn=123456789,
            publication_date='2025-01-01'
        )
        self.book.genre.set([self.genre]) 
        FavoriteBook.objects.create(user=self.user, book=self.book)

    def test_book_list_view(self):
        response = self.client.get(reverse('book_list')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertContains(response, 'Тестовая Книга')
        self.assertIn(self.book.pk, response.context['favorite_books'])

class AuthorListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass') 
        self.client.login(username='testuser', password='testpass') 
        self.author = Author.objects.create(
            first_name='Тестовый',
            last_name='Автор',
            biography='Биография тестового автора'
        )

    def test_author_list_view(self):
        response = self.client.get(reverse('author_list')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'author_list.html')
        self.assertContains(response, 'Тестовый')  
        self.assertContains(response, 'Автор') 
        self.assertContains(response, 'Биография тестового автора')  
        self.assertEqual(len(response.context['authors']), 1) 


class GenreListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass') 
        self.client.login(username='testuser', password='testpass') 
        self.genre = Genre.objects.create(name='Тестовый Жанр')

    def test_genre_list_view(self):
        response = self.client.get(reverse('genre_list'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'genre_list.html')
        self.assertContains(response, 'Тестовый Жанр')


class BookDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass') 
        self.client.login(username='testuser', password='testpass') 
    
        self.author = Author.objects.create(
            first_name='Тестовый',
            last_name='Автор',
            biography='Биография тестового автора'
        )
        

        self.genre = Genre.objects.create(name='Тестовый жанр') 
        

        self.book = Book.objects.create(
            title='Тестовая Книга',
            summary='Описание тестовой книги',
            isbn='1234567890123',
            publication_date='2025-01-01'
        )
        self.book.author.add(self.author) 
        self.book.genre.add(self.genre)

    def test_book_detail_view(self):
        response = self.client.get(reverse('book_detail', kwargs={'pk': self.book.pk})) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail.html')
        self.assertEqual(response.context['book'], self.book) 
        self.assertContains(response, 'Тестовая Книга') 
        self.assertContains(response, 'Описание тестовой книги')  
        self.assertContains(response, 'Тестовый Автор') 
        self.assertContains(response, 'Тестовый жанр')



class AuthorDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass') 
        self.client.login(username='testuser', password='testpass') 
        self.author = Author.objects.create(
            first_name='Тестовый',
            last_name='Автор',
            biography='Биография тестового автора'
        )

    def test_author_detail_view(self):
        response = self.client.get(reverse('author_detail', kwargs={'pk': self.author.pk})) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'author_detail.html')
        self.assertEqual(response.context['author'], self.author)
        self.assertContains(response, 'Тестовый Автор') 
        self.assertContains(response, 'Биография тестового автора')



class BookUpdateViewTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name='Тестовый',
            last_name='Автор',
            biography='Биография тестового автора',
            date_of_birth='2000-01-01'
        )
        self.book = Book.objects.create(
            title='Тестовая Книга',
            summary='Краткое содержание книги',
            isbn=9876543210123, 
            publication_date='2022-01-01'
        )
        self.book.author.set([self.author])

    def test_book_update_view(self):
        response = self.client.post(reverse('book_update', kwargs={'pk': self.book.pk}), {
            'title': 'Обновленная Книга',
            'summary': 'Обновленное краткое содержание',
            'isbn': 9876543210987,  
            'publication_date': '2023-01-01',
            'authors': [self.author.pk],
            'genres': []  
        })

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Обновленная Книга')
        self.assertEqual(self.book.isbn, 9876543210987)



class AuthorUpdateViewTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name='Тестовый',
            last_name='Автор',
            biography='Биография тестового автора',
            date_of_birth='2000-01-01'
        )

    def test_author_update_view(self):
        response = self.client.post(reverse('author_update', kwargs={'pk': self.author.pk}), {
            'first_name': 'Обновленный',
            'last_name': 'Автор',
            'biography': 'Обновленная биография автора', 
            'date_of_birth': '2000-01-01',
            'date_of_death': '',  
        })
        
        self.author.refresh_from_db()
        self.assertEqual(self.author.first_name, 'Обновленный')
        self.assertEqual(self.author.last_name, 'Автор')


class AddToFavoritesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Тестовая книга', summary='Краткое содержание книги', isbn='1234567890123', publication_date='2023-01-01')

    def test_add_book_to_favorites(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('add_to_favorites', args=[self.book.id]))
        self.assertRedirects(response, reverse('book_list'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), f'Книга "{self.book.title}" добавлена в избранное!')


    def test_add_existing_book_to_favorites(self):
        self.client.force_login(self.user)
        self.user.favoritebook_set.create(book=self.book)  
        response = self.client.post(reverse('add_to_favorites', args=[self.book.id]))
        self.assertRedirects(response, reverse('book_list'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), f'Книга "{self.book.title}" уже есть в избранном!')




class FavoriteBookListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_favorite_books_list_view(self):
        book1 = Book.objects.create(title='Тестовая книга 1', summary='Краткое содержание 1', isbn='1234567890123', publication_date='2023-01-01')
        book2 = Book.objects.create(title='Тестовая книга 2', summary='Краткое содержание 2', isbn='9876543210123', publication_date='2023-02-01')
        FavoriteBook.objects.create(user=self.user, book=book1)
        FavoriteBook.objects.create(user=self.user, book=book2)

        response = self.client.get(reverse('favorite_books'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favorite_books.html')
        self.assertEqual(len(response.context['favorite_books']), 2)


class RemoveFromFavoritesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(
            title='Тестовая книга',
            summary='Краткое содержание книги',
            isbn='1234567890123',
            publication_date='2023-01-01'
        )
        self.favorite = FavoriteBook.objects.create(user=self.user, book=self.book)
        self.client.login(username='testuser', password='testpassword')

    def test_remove_book_from_favorites(self):
        self.client.force_login(self.user)
        favorite, created = FavoriteBook.objects.get_or_create(user=self.user, book=self.book)
        response = self.client.post(reverse('remove_from_favorites', args=[favorite.id]))
        self.assertRedirects(response, reverse('favorite_books'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Книга была удалена из избранных.")


# --------------------------------------------------------------------------------------------



class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')

class AuthorModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='John', last_name='Doe', biography='Some biography')

    def test_author_creation(self):
        self.assertEqual(self.author.first_name, 'John')
        self.assertEqual(self.author.last_name, 'Doe')
        self.assertEqual(self.author.biography, 'Some biography')

class GenreModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name='Fiction')

    def test_genre_creation(self):
        self.assertEqual(self.genre.name, 'Fiction')
        self.assertEqual(Genre.objects.count(), 1)

class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='John', last_name='Doe', biography='Some biography')
        self.genre = Genre.objects.create(name='Fiction')
        self.book = Book.objects.create(title='Test Book', isbn=1234567890, publication_date='2025-01-01')
        self.book.author.add(self.author)
        self.book.genre.add(self.genre)

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.isbn, 1234567890)
        self.assertEqual(self.book.author.first(), self.author) 
        self.assertEqual(self.book.genre.first(), self.genre)

class FavoriteBookModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.author = Author.objects.create(first_name='John', last_name='Doe', biography='Some biography')
        self.genre = Genre.objects.create(name='Fiction')
        self.book = Book.objects.create(title='Test Book', isbn=1234567890, publication_date='2025-01-01')
        self.book.author.add(self.author)
        self.book.genre.add(self.genre)
        self.favorite_book = FavoriteBook.objects.create(user=self.user, book=self.book)

    def test_favorite_book_creation(self):
        self.assertEqual(self.favorite_book.user, self.user)
        self.assertEqual(self.favorite_book.book, self.book)

    def test_unique_constraint(self):
        with self.assertRaises(Exception) as context:
            FavoriteBook.objects.create(user=self.user, book=self.book)
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))


# ----------------------------------------------------------------------------------


class CeleryTasksTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_send_daily_new_books(self):
        new_book = Book.objects.create(
            title='New Book',
            isbn=1234567890,
            publication_date=timezone.now() - timedelta(hours=1)
        )

        send_daily_new_books()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Новые книги за последние 24 часа')
        self.assertIn(new_book.title, mail.outbox[0].body)

    def test_send_anniversary_books(self):
        anniversary_book = Book.objects.create(
            title='Anniversary Book',
            isbn=1234567891,
            publication_date=timezone.now() - timedelta(days=5 * 365)
        )
        send_anniversary_books()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Юбилей книги!')
        self.assertIn(anniversary_book.title, mail.outbox[0].body)