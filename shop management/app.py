import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='owner', lazy=True)
    tickets = db.relationship('Ticket', foreign_keys='Ticket.user_id', backref='creator', lazy=True)
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assigned_to_id', backref='assignee', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='ticket', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # product, ticket, user
    description = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reference_id = db.Column(db.Integer)  # ID of the related entity (product, ticket, etc.)

# Helper functions
def log_activity(activity_type, description, reference_id=None):
    if current_user.is_authenticated:
        activity = Activity(
            type=activity_type,
            description=description,
            user_id=current_user.id,
            reference_id=reference_id
        )
        db.session.add(activity)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Make the first user an admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user-guide')
def user_guide():
    return render_template('user_guide.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent products (last 5)
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    
    # Get recent tickets (last 5)
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
    
    # Get recent activities (last 10)
    recent_activities = Activity.query.order_by(Activity.timestamp.desc()).limit(10).all()
    
    # Count products
    total_products = Product.query.count()
    in_stock_products = Product.query.filter(Product.stock > 0).count()
    low_stock_products = Product.query.filter(Product.stock > 0, Product.stock < 10).count()
    
    # Count open tickets
    open_tickets = Ticket.query.filter(Ticket.status != 'closed').count()
    
    return render_template('dashboard.html', 
                          recent_products=recent_products,
                          recent_tickets=recent_tickets,
                          recent_activities=recent_activities,
                          total_products=total_products,
                          in_stock_products=in_stock_products,
                          low_stock_products=low_stock_products,
                          open_tickets=open_tickets)

@app.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of products per page
    
    # Get filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    stock_filter = request.args.get('stock', '')
    
    # Base query
    query = Product.query
    
    # Apply filters
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | 
                           Product.description.ilike(f'%{search}%'))
    
    if category:
        query = query.filter(Product.category == category)
    
    if stock_filter:
        if stock_filter == 'in_stock':
            query = query.filter(Product.stock > 0)
        elif stock_filter == 'low_stock':
            query = query.filter(Product.stock > 0, Product.stock < 10)
        elif stock_filter == 'out_of_stock':
            query = query.filter(Product.stock == 0)
    
    # Get paginated products
    paginated_products = query.order_by(Product.name).paginate(page=page, per_page=per_page, error_out=False)
    products = paginated_products.items
    total_pages = paginated_products.pages
    
    # Get all unique categories for the filter dropdown
    categories = db.session.query(Product.category).filter(Product.category != None, Product.category != '').distinct().order_by(Product.category).all()
    categories = [category[0] for category in categories]
    
    return render_template('products.html', 
                          products=products, 
                          categories=categories,
                          page=page,
                          total_pages=total_pages)

@app.route('/tickets')
@login_required
def tickets():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of tickets per page
    
    # Get filter parameters
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    
    # Base query
    query = Ticket.query
    
    # Apply filters
    if search:
        query = query.filter(Ticket.title.ilike(f'%{search}%') | 
                           Ticket.description.ilike(f'%{search}%'))
    
    if status:
        query = query.filter(Ticket.status == status)
    
    if priority:
        query = query.filter(Ticket.priority == priority)
    
    # Get paginated tickets
    paginated_tickets = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    tickets = paginated_tickets.items
    total_pages = paginated_tickets.pages
    
    return render_template('tickets.html', 
                          tickets=tickets,
                          page=page,
                          total_pages=total_pages)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        image_url = request.form.get('image_url')
        
        # Validate inputs
        if not name or not price or not stock:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('add_product'))
        
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash('Price must be a number and stock must be an integer', 'danger')
            return redirect(url_for('add_product'))
        
        # Create new product
        product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            stock=stock,
            image_url=image_url
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Log activity
        log_activity('product_add', f'Added new product: {name}', product.id)
        
        flash('Product added successfully', 'success')
        return redirect(url_for('products'))
    
    return render_template('add_product.html')

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        
        try:
            product.price = float(request.form.get('price'))
            product.stock = int(request.form.get('stock'))
        except ValueError:
            flash('Price must be a number and stock must be an integer', 'danger')
            return redirect(url_for('edit_product', product_id=product_id))
        
        product.image_url = request.form.get('image_url')
        
        db.session.commit()
        
        # Log activity
        log_activity('product_edit', f'Updated product: {product.name}', product.id)
        
        flash('Product updated successfully', 'success')
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    
    db.session.delete(product)
    db.session.commit()
    
    # Log activity
    log_activity('product_delete', f'Deleted product: {product_name}', product_id)
    
    flash('Product deleted successfully', 'success')
    return redirect(url_for('products'))

@app.route('/tickets/add', methods=['GET', 'POST'])
@login_required
def add_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        
        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            status='open',
            user_id=current_user.id
        )
        
        # Assign to user if specified
        assigned_to = request.form.get('assigned_to')
        if assigned_to and assigned_to != '':
            ticket.assigned_to_id = int(assigned_to)
        
        db.session.add(ticket)
        db.session.commit()
        
        # Log activity
        log_activity('ticket_create', f'Created ticket: {title}', ticket.id)
        
        flash('Ticket created successfully', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket.id))
    
    # Get all users for assignee dropdown
    users = User.query.all()
    return render_template('add_ticket.html', users=users)

@app.route('/tickets/view/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Handle comment submission
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            comment = Comment(
                content=content,
                ticket_id=ticket.id,
                user_id=current_user.id
            )
            db.session.add(comment)
            db.session.commit()
            
            # Log activity
            log_activity('comment_add', f'Added comment to ticket: {ticket.title}', ticket.id)
            
            flash('Comment added successfully', 'success')
            return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    # Find related tickets (same status or priority)
    related_tickets = Ticket.query.filter(
        (Ticket.status == ticket.status) | (Ticket.priority == ticket.priority),
        Ticket.id != ticket.id
    ).limit(5).all()
    
    return render_template('view_ticket.html', ticket=ticket, related_tickets=related_tickets)

@app.route('/tickets/edit/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if request.method == 'POST':
        ticket.title = request.form.get('title')
        ticket.description = request.form.get('description')
        ticket.priority = request.form.get('priority')
        ticket.status = request.form.get('status')
        
        # Update assignee if specified
        assigned_to = request.form.get('assigned_to')
        if assigned_to and assigned_to != '':
            ticket.assigned_to_id = int(assigned_to)
        else:
            ticket.assigned_to_id = None
        
        db.session.commit()
        
        # Log activity
        status_change = f' (Status: {ticket.status})' if ticket.status else ''
        log_activity('ticket_edit', f'Updated ticket: {ticket.title}{status_change}', ticket.id)
        
        flash('Ticket updated successfully', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    # Get all users for assignee dropdown
    users = User.query.all()
    return render_template('edit_ticket.html', ticket=ticket, users=users)

@app.route('/tickets/delete/<int:ticket_id>')
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket_title = ticket.title
    
    db.session.delete(ticket)
    db.session.commit()
    
    # Log activity
    log_activity('ticket_delete', f'Deleted ticket: {ticket_title}', ticket_id)
    
    flash('Ticket deleted successfully', 'success')
    return redirect(url_for('tickets'))

@app.route('/tickets/close/<int:ticket_id>', methods=['POST'])
@login_required
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = 'closed'
    db.session.commit()
    
    # Log activity
    log_activity('ticket_close', f'Closed ticket: {ticket.title}', ticket.id)
    
    flash('Ticket marked as closed', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate username and email
        if not username or not email:
            flash('Username and email are required', 'danger')
            return redirect(url_for('profile'))
        
        # Check if another user already has this username or email
        user_with_username = User.query.filter(User.username == username, User.id != current_user.id).first()
        user_with_email = User.query.filter(User.email == email, User.id != current_user.id).first()
        
        if user_with_username:
            flash('Username already taken', 'danger')
            return redirect(url_for('profile'))
        
        if user_with_email:
            flash('Email already in use', 'danger')
            return redirect(url_for('profile'))
        
        # Update username and email
        current_user.username = username
        current_user.email = email
        
        # Update password if provided
        if current_password and new_password and confirm_password:
            # Verify current password
            if not check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('profile'))
            
            # Verify new passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('profile'))
            
            # Update password
            current_user.password = generate_password_hash(new_password)
            
            # Log activity
            log_activity('password_change', 'Changed password')
            
            flash('Password updated successfully', 'success')
        
        db.session.commit()
        
        # Log activity
        log_activity('profile_update', 'Updated profile information')
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # Get user's recent activities
    user_activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).limit(10).all()
    
    return render_template('profile.html', user_activities=user_activities)

# API routes
@app.route('/api/products', methods=['GET'])
def api_products():
    products = Product.query.all()
    result = []
    
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'category': product.category
        })
    
    return jsonify(result)

@app.route('/api/tickets', methods=['GET'])
@login_required
def api_tickets():
    tickets = Ticket.query.all()
    result = []
    
    for ticket in tickets:
        result.append({
            'id': ticket.id,
            'title': ticket.title,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_by': ticket.user_id,
            'assigned_to': ticket.assigned_to_id,
            'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create admin user if no users exist
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
