from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import *
from django.utils import timezone

# Create your views here.
BASE_FINE = 2 #fine per day in INR

def home(request):
    period = 'morning'
    cont1 = footer_counter()
    hours = int(str(timezone.now().time()).split(':')[0]) #returns the current hour
    if hours >= 18:
        period = 'evening'
    elif hours >= 12:
        period = 'afteroon'
    late_ret = IssuedBooks.objects.filter(due_date__lt=timezone.now().date())
    upcoming_ret = IssuedBooks.objects.filter(due_date__gte=timezone.now().date())
    cont2 = {'daytime': period.title(), 'passed_dues': late_ret, 'future_dues': upcoming_ret}
    return render(request, 'home.html', {**cont1, **cont2})

def members(request):
    cont1 = footer_counter()
    cont2 = {
        'members': Members.objects.all().order_by('-id'),
        'form': AddMembers(),
    }
    if request.method == 'GET':
        return render(request, "members.html", {**cont1, **cont2})
    if request.method == 'POST':
        data = AddMembers(request.POST)
        if data.is_valid():
            if len(data.cleaned_data['phone_no']) != 10:
                return render(request, "members.html", {**cont1, **cont2, 'msg': 'Phone number should be 10 digits long'})
            else:
                data.save()
        return redirect(members)

def mem_log(request, pk):
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import mm
    
    memb = get_object_or_404(Members, id=pk)
    
    # Render the template with the context data
    actions = get_actions(pk,memb)

    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Set the font and title of the document
    pdf.setFont("Helvetica",12)
    pdf.setTitle(f"{memb.getName()} Activity Log")

    # get the width and height of the page
    width, height = pdf._pagesize

    # Draw the rendered HTML content on the PDF
    pdf.drawString(10*mm, 270*mm, f'This is an auto generated activity log for {memb.getName()}:')
    pdf.drawString(2*mm, 260*mm, '-' * 150)
    DIST = 250
    
    # Printing current issues
    if actions[1]:
        pdf.drawString(3.5*mm, DIST*mm, f'Current Issues:'); DIST -= 10
        for action in actions[1]:
            pdf.drawString(5*mm, DIST*mm, f'[{action[0].strftime("%d/%m/%Y %H:%M")}]: Book issue - "{action[1]}"')
            DIST -= 10
            pdf.drawString(43*mm, DIST*mm, f'ISBN: {action[2]} || Issue ID: {action[3]}')
            DIST -= 10
        pdf.drawString(2*mm, DIST*mm, '-' * 150); DIST -= 10
    
    # Printing Issue-Return History
    pdf.drawString(3.5*mm, DIST*mm, f'Past Entries:'); DIST -= 10
    pdf.drawString(5*mm, DIST*mm, f'[{memb.memb_since.strftime("%d/%m/%Y %H:%M")}]: Registered as Member [ID: {pk}]')
    DIST -= 10
    
    for action in actions[0]:
        pdf.drawString(5*mm, DIST*mm, f'[{action[0].strftime("%d/%m/%Y %H:%M")}]: Book {action[1]} - "{action[2]}"')
        DIST -= 10
        pdf.drawString(43*mm, DIST*mm, f'ISBN: {action[3]} || Issue ID: {action[4]}')
        DIST -= 10

    pdf.drawString(2*mm, DIST*mm, '-' * 150); DIST -= 2
    pdf.drawString(2*mm, DIST*mm, '-' * 150)
    
    # Close the PDF object cleanly, and we're done.
    pdf.showPage()
    pdf.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
    
def issued_books(request):
    if request.method == 'GET':
        cont1 = footer_counter()
        cont2 = {
            'form': BookIssueForm(),
            'issues': IssuedBooks.objects.all().order_by('-id')
        }
        return render(request,"issued.html",{**cont1, **cont2})
    if request.method == 'POST':
        data = BookIssueForm(request.POST)
        if data.is_valid():
            data.save()
        return redirect(issued_books)

def return_book(request, id):
    issued_book = get_object_or_404(IssuedBooks, pk=id)
    delay = timezone.now().date() - issued_book.due_date
    if delay.days < 1:
        issued_book.set_returned()
    else:
        return pay_fine(request, id, delay.days)
    return redirect(issued_books)    

def pay_fine(request, issue_id, delay):
    issue = get_object_or_404(IssuedBooks,pk=issue_id)
    if request.method == 'GET':
        fine_amt = BASE_FINE * delay
        cont1 = footer_counter()
        cont2 = {'issue': issue, 'days': delay, 'fine': fine_amt}
        return render(request, 'return_fine.html', {**cont1, **cont2})
    if request.method == 'POST':
        if request.POST.get("fine_paid", 0):
            issue.set_returned()
            return redirect(returned_books)

def returned_books(request):
    cont1 = footer_counter()
    cont2 = {
        'returns': ReturnedBooks.objects.all().order_by('-returned')
    }
    return render(request,"returned.html",{**cont1, **cont2})

def mem_delete(request, pk):
    mem = get_object_or_404(Members, id=pk)
    try:
        mem.delete()
    except:
        cont1 = footer_counter()
        cont2 = {
            'msg': "Pending issues to be returned. Try again after all books are returned",
            'issues': IssuedBooks.objects.filter(member_id=pk).order_by('-issue_date')
        }
        return render(request,"issued.html",{**cont1, **cont2})
    return redirect(members)

def books(request):
    cont1 = footer_counter()
    cont2 = {'books': Books.objects.all().order_by("bookName")}
    return render(request, 'books.html', {**cont1,**cont2})

def add_book(request):
    if request.method == "GET":
        cont1 = footer_counter()
        cont2 = {'bookform': AddBooks(), 'authform': AddAuthors(), 'pubform': AddPubs()}
        return render(request, 'add_book.html', {**cont1,**cont2})
    if request.method == "POST":
        bookData = AddBooks(request.POST)
        authData = AddAuthors(request.POST)
        pubData = AddPubs(request.POST)
        if bookData.is_valid():
            bookData.save()
        elif authData.is_valid():
            authData.save()
        elif pubData.is_valid():
            pubData.save()
        return redirect(add_book)

def book_details(request, pk):
    book = get_object_or_404(Books, isbn=pk)
    if request.method == 'GET':
        cont1 = footer_counter()
        return render(request, 'book_details.html', {**cont1, "book": book})
    if request.method == 'POST':
        upInv = int(request.POST.get('upInv',0))
        if upInv != 0:
            if not (book.inventory == 0 and upInv == -1):
                book.inventory += upInv
                book.save()
        return redirect(book_details, pk=pk)

def book_delete(request, pk):
    book = get_object_or_404(Books, isbn=pk)
    try:
        book.delete()
    except:
        cont1 = footer_counter()
        cont2 = {
            'msg': "Books pending to be returned. Try again after all books are returned.",
            'issues': IssuedBooks.objects.filter(book_id=pk).order_by('-issue_date')
        }
        return render(request,"issued.html",{**cont1, **cont2})
    return redirect(books)

# helper functions
def footer_counter(): # Get reqd count values to display in footer 
    tot_books = 0
    for book in list(Books.objects.all()):
        tot_books = tot_books + book.inventory
    context = {
        'tot_mem': Members.objects.all().count(),
        'no_books': Books.objects.all().count(),
        'tot_books': tot_books,
        }
    return context

def get_actions(pk, memb): # Get actions sorted by date
    retiss_act = list(ReturnedBooks.objects.filter(member_id=pk).order_by("issue_date"))
    ret_act = list(ReturnedBooks.objects.filter(member_id=pk).order_by("returned"))
    past_act, i_ptr, r_ptr = [], 0, 0
    while i_ptr < len(retiss_act) and r_ptr < len(ret_act):
        if(retiss_act[i_ptr].issue_date <= ret_act[r_ptr].returned):
            past_act.append((retiss_act[i_ptr].issue_date,'issue',retiss_act[i_ptr].book,retiss_act[i_ptr].book_isbn,retiss_act[i_ptr].issue_id))
            i_ptr += 1
        else:
            past_act.append((ret_act[r_ptr].returned,'return',ret_act[r_ptr].book, ret_act[r_ptr].book_isbn,ret_act[r_ptr].issue_id))
            r_ptr += 1
    while i_ptr < len(retiss_act):
        past_act.append((retiss_act[i_ptr].issue_date,'issue',retiss_act[i_ptr].book,retiss_act[i_ptr].book_isbn,retiss_act[i_ptr].issue_id))
        i_ptr += 1
    while r_ptr < len(ret_act):
        past_act.append((ret_act[r_ptr].returned,'return',ret_act[r_ptr].book, ret_act[r_ptr].book_isbn,ret_act[r_ptr].issue_id))
        r_ptr += 1
    
    # current issues
    curr_acts = list(IssuedBooks.objects.filter(member=memb).order_by("issue_date"))
    curr_act = []
    for act in curr_acts:
        curr_act.append((act.issue_date,act.book.getName(),act.book.isbn,act.pk))
    return (past_act, curr_act)  # returns a list of activities in the form of
                    # a Tuple: (Date, Action, Book Name, Book ISBN, Issue_ID) 
    pass