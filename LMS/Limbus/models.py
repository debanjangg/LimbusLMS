from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


# set the timezone for the current request or process to IST
import pytz
timezone.activate(pytz.timezone('Asia/Kolkata'))

# Create your models here.
class Members(models.Model):
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    phone_no = models.CharField(max_length=10,unique=True)
    email = models.EmailField(blank=True,null=True,unique=True)
    memb_since = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.pk} || {self.getName()}"
    
    def getName(self):
        return f"{self.firstName.title()} {self.lastName.title()}"
    
    def save(self):
        if len(str(self.phone_no)) != 10:
            raise ValueError("Phone number should be of 10 digits")
        self.firstName = self.firstName.casefold()
        self.lastName = self.lastName.casefold()
        self.email = self.email.casefold()
        super().save()

class Authors(models.Model):
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.firstName.title()} {self.lastName.title()}"
    
    def save(self):
        self.firstName = self.firstName.casefold()
        self.lastName = self.lastName.casefold()
        super().save()
    
class Publishers(models.Model):
    pubName = models.CharField(max_length=40)
    
    def __str__(self):
        return self.pubName.title()
    
    def save(self):
        self.pubName = self.pubName.casefold()
        super().save()

class Books(models.Model):
    isbn = models.BigIntegerField(primary_key=True, validators=[
        MinValueValidator(9780000000000),
        MaxValueValidator(9799999999999),
    ])
    bookName = models.CharField(max_length=50)
    authors = models.ManyToManyField(Authors, through='BookAuth')
    publisher = models.ForeignKey(Publishers, on_delete=models.PROTECT)
    inventory = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.pk} || {self.getName()}"
    
    def getName(self):
        name, bname = self.bookName.split(), ""
        for x in name:
            bname += x[0].upper() + x[1:] + " "
        return bname[:-1]
    
    def getAuthors(self):
        bookAuths = BookAuth.objects.filter(isbn=self.isbn)
        auth = ""
        for bookAuth in bookAuths:
            auth += f"{bookAuth.getAuth()}, "
        return auth[:-2]
    
    def save(self):
        self.bookName = self.bookName.casefold()
        super().save()

class BookAuth(models.Model):
    isbn = models.ForeignKey(Books, on_delete=models.CASCADE)
    auth = models.ForeignKey(Authors, on_delete=models.PROTECT)
    
    def getAuth(self):
        return Authors.objects.get(id=self.auth.id)
    
    def __str__(self):
        return f"{self.auth} - {self.isbn}"

class IssuedBooks(models.Model):
    member = models.ForeignKey(Members, on_delete=models.PROTECT)
    book = models.ForeignKey(Books, on_delete=models.PROTECT)
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()

    class Meta:
        unique_together = ('member', 'book')
    
    def __str__(self):
        return f'{self.member.firstName[0].capitalize()}. {self.member.lastName.title()} - {self.book.bookName.title()}'
        
    def save(self):
        if not self.pk: # if self.pk is None
            # Check if the member already has 2 issued books
            if IssuedBooks.objects.filter(member=self.member).count() >= 2:
                raise ValueError('This member already has 2 issued books')
            # reduces inventory count during issue and saves to db
            self.book.inventory -= 1
            self.book.save()
            # sets return date 30days since date of issue
            self.due_date = self.issue_date + timezone.timedelta(days=30)
        super().save()

    def set_returned(self):
        self.book.inventory += 1 # increments the inventory by 1
        self.book.save() # saves updated inventory to db
        # creates a new entry for the ReturnedBooks table
        ret_book = ReturnedBooks(issue_id=self.pk,member=self.member.getName(),member_id=self.member.id, book_isbn = self.book.isbn,
                                 issue_date=self.issue_date,due_date=self.due_date,book=self.book.getName()) 
        ret_book.save() # saves entry to ReturnedBooks table
        self.delete() # deletes entry from IssuedBooks table
        
class ReturnedBooks(models.Model):
    issue_id = models.IntegerField(primary_key=True)
    member = models.CharField(max_length=50)
    member_id = models.IntegerField()
    book = models.CharField(max_length=60)
    book_isbn = models.CharField(max_length=13)
    issue_date = models.DateTimeField()
    due_date = models.DateField()
    returned = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Issue: {self.issue_id} || Returned on: {self.returned}"