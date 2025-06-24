# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(*roles):
    """
    A decorator that ensures the current user has one of the allowed roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the user is logged in by verifying 'role' in session
            if 'role' not in session:
                flash("You must be logged in to access this page.", "error")
                return redirect(url_for('login'))
            # Check if the user's role is among the allowed roles
            if session['role'] not in roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('admin')(f)

def teacher_required(f):
    return role_required('teacher')(f)

def student_required(f):
    return role_required('student')(f)

def community_required(f):
    return role_required('community')(f)
