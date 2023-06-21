from django import forms
from django.forms import CheckboxSelectMultiple
from .models import *
from django.db.models import Count

class AddMembers(forms.ModelForm):
    class Meta:
        model = Members
        fields = ("__all__")

class BookIssueForm(forms.ModelForm):
    member = forms.ModelChoiceField(queryset = Members.objects.annotate(issued_books_count = Count('issuedbooks')).filter(issued_books_count__lt = 2).order_by("id"))
    book = forms.ModelChoiceField(queryset = Books.objects.filter(inventory__gte=1).order_by('isbn'))
    class Meta:
        model = IssuedBooks
        fields = ("member","book")

class AddAuthors(forms.ModelForm):
    class Meta:
        model = Authors
        fields = ("__all__")
        
class AddPubs(forms.ModelForm):
    class Meta:
        model = Publishers
        fields = ("__all__")

class AddBooks(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Authors.objects.all().order_by('firstName','lastName'),
        widget=CheckboxSelectMultiple,
        )
    publisher = forms.ModelChoiceField(queryset=Publishers.objects.all().order_by("pubName"))
    class Meta:
        model = Books
        fields = ('isbn', 'bookName', 'authors', 'publisher', 'inventory')