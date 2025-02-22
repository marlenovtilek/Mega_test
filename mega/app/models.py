from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name='Электронная почта', unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
    

class Author(models.Model):
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    biography = models.TextField("Биография")
    date_of_birth = models.DateField("Дата рождения", null=True, blank=True)
    date_of_death = models.DateField("Дата смерти", null=True, blank=True)

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField("Название", max_length=100)
    summary = models.TextField("Краткое содержание", blank=True, null=True)
    isbn = models.IntegerField("ISBN", unique=True)
    author = models.ManyToManyField(Author, verbose_name="Автор")
    publication_date = models.DateField("Дата публикации")
    genre = models.ManyToManyField(Genre, verbose_name="Жанр")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title
    

class FavoriteBook(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="Пользователь", on_delete=models.CASCADE)
    book = models.ForeignKey(Book, verbose_name="Книги", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Избранная книга"
        verbose_name_plural = "Избранные книги"
        unique_together = ('user', 'book')


    def __str__(self):
        return self.user.username