from flask_login import LoginManager, UserMixin, current_user
from flask import flash, redirect, url_for, request
from functools import wraps
from models.user import User

# Create LoginManager instance
login_manager = LoginManager()

# Configure LoginManager
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def login_required(f):
    """Decorator that requires a user to be logged in to access a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(user_id)

# Add Flask-Login methods to User model
def init_user_auth_methods():
    """Initialize authentication methods for User model"""
    
    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return True
    
    def is_active(self):
        """Return True if the user is active"""
        return True
    
    def is_anonymous(self):
        """Return False as this is not an anonymous user"""
        return False
    
    def get_id(self):
        """Return the user ID as a string"""
        return str(self.id)
    
    # Add methods to User class
    User.is_authenticated = is_authenticated
    User.is_active = is_active
    User.is_anonymous = is_anonymous
    User.get_id = get_id
