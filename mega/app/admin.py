from django.contrib import admin
from app.models import Author, Book, CustomUser, FavoriteBook

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(FavoriteBook)