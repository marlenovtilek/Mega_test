from django import forms

from app.models import Author, Book, Genre


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'biography', 'date_of_birth', 'date_of_death']
 
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'summary', 'isbn', 'author', 'publication_date', 'genre']

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']