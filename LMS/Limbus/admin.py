from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Members)
admin.site.register(Books)
admin.site.register(Authors)
admin.site.register(BookAuth)
admin.site.register(IssuedBooks)
admin.site.register(ReturnedBooks)