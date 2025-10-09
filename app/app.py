from flask import Flask, request, render_template, redirect, url_for, flash
from app.model import Book, db_with_books, User, LoginForm, RegForm, NewBookForm
from flask_login import login_user, logout_user, login_required, current_user
from app import app

# Define a admin required
from functools import wraps
from flask import abort

def admin_required(f):
    """
    Restricts access to the decorated route to authenticated users whose 
    email is 'admin@lib.sg'. Uses the new is_admin property on the User model.
    """
    # The original decorator used wraps and decorated_function, so we keep that structure.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # We check the is_admin property, which now handles the email check.
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. You must be the administrator to view this page.', 'danger')
            
            # Use redirect for better user experience instead of raw abort(403)
            if current_user.is_authenticated:
                # Logged in but not admin
                return redirect(url_for('book_titles')) 
            else:
                # Not logged in at all
                return redirect(url_for('login')) 
            
        return f(*args, **kwargs)
    return decorated_function


def get_unique_categories():
    """
    Retrieves a sorted list of unique categories directly from the MongoDB collection.
    """
    # Use MongoEngine's distinct method which translates to MongoDB's distinct command
    categories_cursor = Book.objects.distinct('category')
    
    # MongoEngine returns a list of distinct values
    unique_categories = sorted(categories_cursor)
    
    return unique_categories

def get_book_by_title(title):
    """
    Retrieves a book document from the MongoDB collection by its title.
    """
    book = Book.objects(title=title).first()  # Use .first() to get a single document or None
    return book

@app.route('/')

@app.route('/book_titles')
def book_titles():
    # use the db_with_books to populate the database and retrieve all books
    #db_with_books()  # Ensure the database is populated with books

    # 1. get the selected category from the request
    selected_category = request.args.get('category', 'All')

    # 2. start a mongodb query 
    query = Book.objects()

    # 3. filter the books if a specific category is selected
    if selected_category != 'All':
         #filter mongoengine uses keyword arguments for filtering
        query = query.filter(category=selected_category)

    sorted_books = query.order_by('title') # sort alphabetically by title
    unique_categories = get_unique_categories() # get unique categories for the dropdown

    return render_template(
        'book_titles.html', 
        books=sorted_books,
        selected_category=selected_category,
        unique_categories=unique_categories 
    )

@app.route('/book/<string:book_title>') #book detail page
def book_detail(book_title):
    """
    Fetches a single book from the database using its title.
    """
    try:
        book = Book.objects.get(title=book_title) #get the book by title

    except Book.DoesNotExist:
        #case where the book is not found in the database
        return render_template('404.html'), 404 
    
    #pass the MongoEngine document object 'book' to the template
    return render_template('book_detail.html', book=book) 


#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('book_titles'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data 

        # 1. Find the user by email
        user = User.objects(email=email).first()
        
        # 2. Check if user exists AND the password hash matches
        # The User model now has a check_password method using check_password_hash
        if user and user.check_password(password): 
            login_user(user, remember=remember) # remember me functionality
            
            # 3. Redirect to the requested page or home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('book_titles')) 
        else:
            # Invalid credentials. The form will re-render without a flash message.
            pass

    return render_template("login.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('book_titles'))

    form = RegForm()
    if form.validate_on_submit():
        name = form.username.data
        
        # User.save_user now handles hashing the password before saving
        new_user = User.save_user(name=name, password=form.password.data, email=form.email.data)
        
        if new_user: 
            # Successful registration, redirect to login
            return redirect(url_for('login')) 
        else:
            # User already exists or error. The form will re-render without a flash message.
            pass
        
    return render_template("register.html", form=form)

@app.route('/logout')
@login_required # Requires the user to be logged in to access
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('book_titles'))


#adding book, admin only
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    """
    Handles adding a new book to the database.
    """
    form = NewBookForm()
    while len(form.new_book_authors.entries) < 5:
        form.new_book_authors.append_entry()

    if form.validate_on_submit():
        authors = []
        for entry in form.new_book_authors.data:
            author_name = entry['name'].strip()
            is_illustrator = entry['is_illustrator']
            
            if author_name:
                if is_illustrator:
                    authors.append(f"{author_name} (Illustrator)") # Changed for clarity
                else:
                    authors.append(author_name)
        

        genre_list = [g.strip() for g in form.genres.data]
        description_list = [p.strip() for p in form.description.data.split('\n') if p.strip()]
        
        try:
            new_book = Book(
                title=form.title.data,
                category=form.category.data,
                genres=genre_list,
                url=form.url.data,
                description=description_list,
                authors=authors,
                pages=form.pages.data,
                copies=form.copies.data,
                available=form.copies.data
            )
            new_book.save()
            flash(f'Book "{new_book.title}" added successfully!', 'success')
            return redirect(url_for('book_titles'))
            
        except Exception as e:
            flash(f'An error occurred while saving the book: {e}', 'danger')
            
    return render_template('add_book.html', form=form)

# Making a loan
@app.route('/make_loan/<string:title>', methods=['POST'])
@login_required
def make_loan(title):
    book = Book.objects(title=title).first()
    if book and book.available > 0:
        book.available -= 1
        book.save()
        success, message = book.borrow(current_user)
        flash(message, 'success' if success else 'danger')
    else:
        flash(f'Book "{book.title}" is not available for loan.', 'danger')
    return redirect(url_for('book_titles'))
