from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('members/', views.members, name='members'),
    path('members/<int:pk>', views.mem_log, name='mem_log'),
    path('members/del/<int:pk>', views.mem_delete, name='mem_dlt'),
    path('books/', views.books, name='books'),
    path('add_book/', views.add_book, name='add_book'),
    path('books/<int:pk>', views.book_details, name='book_details'),
    path('books/del/<int:pk>', views.book_delete, name='book_dlt'),
    path('book_issues/', views.issued_books, name='issued_books'),
    path('book_issues/return/<int:id>', views.return_book, name='return_issued_books'),
    path('book_issues/pay_fine/<int:id>', views.pay_fine, name='pay_fine'),
    path('returned_books/', views.returned_books, name='returned_books'),
]
