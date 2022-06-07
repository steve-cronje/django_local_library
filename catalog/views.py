import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

from .forms import RenewBookModelForm
from .models import Book, Author, BookInstance

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_genres_with_fantasy = Book.objects.filter(genre__name__icontains='fantasy').count()
    num_books_with_the = Book.objects.filter(title__icontains='the').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_with_fantasy': num_genres_with_fantasy,
        'num_books_with_the': num_books_with_the,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(ListView):

    model = Book

    context_object_name = 'book_list'   # your own name for the list as a template variable

    def get_queryset(self):
        return Book.objects.all()
    

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['data'] = Book.objects.filter(title__icontains='the')[:5]
        return context
    
    template_name = 'book/books_list.html'
    paginate_by = 10


class BookDetailView(DetailView):

    model = Book
    
    template_name = 'book/book_detail.html'


class AuthorListView(ListView):
    model = Author

    context_object_name = 'author_list'   # your own name for the list as a template variable

    def get_queryset(self):
        return Author.objects.all()
    

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        return context
    
    template_name = 'author/authors_list.html'
    paginate_by = 10


class AuthorDetailView(DetailView):

    model = Author

    template_name = 'author/author_detail.html'


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='book/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='book/bookinstance_list_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'book/book_renew.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_edit_authors'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'author/author_form.html'
    # initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_edit_authors'
    model = Author
    template_name = 'author/author_form.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death'] 
    
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_edit_authors'
    model = Author
    template_name = 'author/author_confirm_delete.html'
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    template_name = 'book/book_form.html'
    # initial = {'date_of_death': '11/06/2020'}

class BookUpdate(UpdateView):
    model = Book
    template_name = 'book/book_form.html'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Author
    template_name = 'book/book_confirm_delete.html'
    success_url = reverse_lazy('books')
