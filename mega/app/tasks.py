from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import Book, CustomUser

@shared_task
def send_daily_new_books():
    """Отправка пользователям списка книг, добавленных за последние 24 часа"""

    print("Запускаем задачу отправки писем!") 

    yesterday = timezone.now() - timedelta(days=1)
    new_books = Book.objects.filter(publication_date__gte=yesterday)

    if new_books.exists():
        users = CustomUser.objects.all()
        book_list = "\n".join([book.title for book in new_books])
        
        for user in users:
            send_mail(
                "Новые книги за последние 24 часа",
                f"Привет, {user.username}!\nВот список новых книг:\n{book_list}",
                "admin@example.com",
                [user.email],
                fail_silently=False,
            )
        print("Письмо отправлено!") 

@shared_task
def send_anniversary_books():
    """Отправка уведомлений пользователям о юбилейных книгах"""


    print("Запускаем задачу отправки писем! годовщина") 

    today = timezone.now().date()
    anniversary_years = [5, 10, 20, 50, 100]

    books = Book.objects.all()
    users = CustomUser.objects.all()

    for book in books:
        years_since_publication = today.year - book.publication_date.year
        if years_since_publication in anniversary_years:
            for user in users:
                send_mail(
                    "Юбилей книги!",
                    f"Привет, {user.username}!\nСегодня юбилей {years_since_publication} лет книги {book.title}.",
                    "admin@example.com",
                    [user.email],
                    fail_silently=False,
                )
            print("Письмо отправлено! годовщина") 
