from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from forms import ReportSightingForm, RegistrationForm, LoginForm
from decorators import admin_required, teacher_required, student_required, community_required

app = Flask(__name__, template_folder='views', static_folder='static')
app.secret_key = 'supersecretkey123'
bcrypt = Bcrypt(app)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join('static', 'uploads')  # "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('UNIT.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    """
    Check if the uploaded file's extension is allowed.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_points(user_id):
    conn = get_db_connection()
    result = conn.execute("SELECT points FROM leaderboard WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return result['points'] if result else 0

# Shared function: Get Endangered Species Data (Static + Dynamic)
def get_endangered_species_data():
    """
    Returns a merged list of static endangered species from the case study
    plus up to 5 dynamic, community-reported species from the database.
    """
    # Static endangered species from the case study
    static_species = [
        {
            'name': 'Komodo Dragon',
            'status': 'Critically Endangered',
            'description': 'The world’s largest lizard found in Indonesia.',
            'image': url_for('static', filename='images/komodo_dragon.avif')
        },
        {
            'name': 'Javan Rhino',
            'status': 'Critically Endangered',
            'description': 'One of the rarest mammals with a very limited habitat in Java, Indonesia.',
            'image': url_for('static', filename='images/javan_rhino.jpeg')
        },
        {
            'name': 'Sumatran Tiger',
            'status': 'Endangered',
            'description': 'The smallest surviving tiger subspecies, threatened by habitat loss and poaching.',
            'image': url_for('static', filename='images/sumatran_tiger.jpeg')
        },
        {
            'name': 'Sumatran Elephant',
            'status': 'Endangered',
            'description': 'A critically endangered elephant species facing habitat fragmentation.',
            'image': url_for('static', filename='images/sumatran_elephant.jpg')
        },
        {
            'name': 'Sumatran Orangutan',
            'status': 'Critically Endangered',
            'description': 'An endangered great ape facing severe habitat loss in Sumatra.',
            'image': url_for('static', filename='images/sumatran_orangutan.jpeg')
        },
        {
            'name': 'Bali Myna',
            'status': 'Critically Endangered',
            'description': 'A bright white bird native to Bali, threatened by illegal trade and habitat loss.',
            'image': url_for('static', filename='images/bali_myna.jpeg')
        }
    ]

    # Fetch dynamic, community-reported species from the database
    conn = get_db_connection()
    reported = conn.execute('''
        SELECT ws.species, ws.location, ws.media_path, ws.notes, ws.timestamp, u.username as uploader
        FROM wildlife_sightings ws
        JOIN users u ON ws.user_id = u.id
        ORDER BY ws.timestamp DESC
        LIMIT 5
    ''').fetchall()
    conn.close()

    dynamic_species = []
    for s in reported:
        # Build a URL for the uploaded file using url_for
        image_url = url_for('static', filename=f"uploads/{s['media_path']}") if s['media_path'] and s['media_path'] != '' else url_for('static', filename='images/default_species.jpg')
        dynamic_species.append({
            'name': s['species'],
            'status': "Community Reported",
            'description': s['notes'] if s['notes'] else f"Sighted at {s['location']}",
            'image': image_url,
            'timestamp': s['timestamp'],
            'uploader': s['uploader']
        })
    return static_species + dynamic_species

# -------------------- Routes --------------------

@app.route('/')
def index():
    """
    Homepage: Displays a summary of endangered species (static + dynamic).
    """
    endangered_species = get_endangered_species_data()
    return render_template('index.html', static_species=endangered_species)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']
        # Convert teacher to admin if selected
        if role.lower() == 'teacher':
            role = 'admin'
        conn = get_db_connection()
        role_row = conn.execute('SELECT id FROM user_roles WHERE role_name = ?', (role,)).fetchone()
        if role_row:
            try:
                conn.execute('INSERT INTO users (username, email, password, role_id) VALUES (?, ?, ?, ?)',
                             (username, email, password, role_row['id']))
                conn.commit()
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username or email already exists.', 'error')
        else:
            flash('Invalid role selected.', 'error')
        conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        conn = get_db_connection()
        user = conn.execute('''
            SELECT users.id, username, password, role_name 
            FROM users 
            JOIN user_roles ON users.role_id = user_roles.id 
            WHERE username = ?
        ''', (username,)).fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            session['user_name'] = user['username']
            session['role'] = user['role_name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logs out the user by clearing the session.
    """
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """
    User dashboard: Displays user points and relevant links.
    """
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    points = get_user_points(session['user_id'])
    return render_template('dashboard.html', points=points)

@app.route('/report_sighting', methods=['GET', 'POST'])
def report_sighting():
    """
    Allows users to report wildlife sightings with optional image upload.
    """
    if 'user_id' not in session:
        flash("You must be logged in to report a sighting.", "error")
        return redirect(url_for('login'))

    form = ReportSightingForm()
    if form.validate_on_submit():
        species = form.species.data
        location = form.location.data
        notes = form.notes.data
        file = form.media.data

        # Save file if present and allowed
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            filename = unique_filename

        # Insert sighting into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO wildlife_sightings (user_id, species, location, media_path, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], species, location, filename, notes))
        conn.commit()

        # Award 10 points for reporting a sighting
        existing = conn.execute('SELECT * FROM leaderboard WHERE user_id = ?', (session['user_id'],)).fetchone()
        if existing:
            conn.execute('UPDATE leaderboard SET points = points + 10 WHERE user_id = ?', (session['user_id'],))
        else:
            conn.execute('INSERT INTO leaderboard (user_id, points) VALUES (?, 10)', (session['user_id'],))
        conn.commit()
        conn.close()

        flash("Sighting submitted successfully! You earned 10 points.", "success")
        return redirect(url_for('dashboard'))

    return render_template('report_sighting.html', form=form)

@app.route('/word_search_game')
def word_search_game():
    """
    Displays the word search game and shows top 10 users on the leaderboard.
    """
    conn = get_db_connection()
    leaderboard = conn.execute('''
        SELECT users.username, leaderboard.points 
        FROM leaderboard
        JOIN users ON users.id = leaderboard.user_id
        ORDER BY points DESC LIMIT 10
    ''').fetchall()
    conn.close()
    return render_template('word_search_game.html', leaderboard=leaderboard)

@app.route('/update_points', methods=['POST'])
def update_points():
    """
    Increments user points by 5 for certain actions (e.g., finishing a game).
    """
    if 'user_id' in session:
        conn = get_db_connection()
        conn.execute('UPDATE leaderboard SET points = points + 5 WHERE user_id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    """
    Messaging system: Allows users to send messages to each other.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        receiver = request.form['receiver']
        content = request.form['content']
        receiver_id = conn.execute('SELECT id FROM users WHERE username = ?', (receiver,)).fetchone()
        if receiver_id:
            conn.execute('INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)',
                         (session['user_id'], receiver_id['id'], content))
            conn.commit()

    messages = conn.execute('''
        SELECT m.*, u1.username AS sender, u2.username AS receiver
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        WHERE m.sender_id = ? OR m.receiver_id = ?
        ORDER BY m.timestamp DESC
    ''', (session['user_id'], session['user_id'])).fetchall()

    users = conn.execute('SELECT username FROM users WHERE id != ?', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('messages.html', messages=messages, users=users)

@app.route('/notifications')
def notifications():
    """
    Notifications page: Shows all notifications for the current user.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    notifications = conn.execute('''
        SELECT * 
        FROM notifications 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', (session['user_id'],)).fetchall()

    # Mark all notifications as read
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()

    return render_template('notifications.html', notifications=notifications)

@app.route('/payments', methods=['GET', 'POST'])
def payments():
    """
    Payment page: Allows users to input donation details and view past transactions.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        amount = request.form.get('amount')
        frequency = request.form.get('frequency')
        plan_name = request.form.get('plan_name', None)
        plan_type = request.form.get('plan_type', 'monthly')

        # Store donation info in session
        session['donation'] = {
            'frequency': frequency,
            'amount': amount,
            'plan_name': plan_name,
            'plan_type': plan_type
        }
        return redirect(url_for('payment_options'))

    transactions = conn.execute('''
        SELECT * 
        FROM payment_transactions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('payments.html', transactions=transactions)

@app.route('/process_donation', methods=['POST'])
def process_donation():
    """
    Processes donation details, storing them in session for the payment options page.
    """
    frequency = request.form.get('frequency')
    amount = request.form.get('amount')
    custom_amount = request.form.get('custom_amount')
    plan_name = request.form.get('plan_name', None)
    plan_type = request.form.get('plan_type', 'monthly')

    final_amount = custom_amount if amount == "other" and custom_amount else amount
    session['donation'] = {
        'frequency': frequency,
        'amount': final_amount,
        'plan_name': plan_name,
        'plan_type': plan_type
    }
    return redirect(url_for('payment_options'))

@app.route('/payment_options')
def payment_options():
    """
    Displays payment options (card, PayPal, Apple Pay, etc.) using data from session.
    """
    donation = session.get('donation', {})
    return render_template('payment_options.html', donation=donation)

@app.route('/card_payment', methods=['GET', 'POST'])
def card_payment():
    """
    Processes a card payment and inserts a record into payment_transactions.
    """
    if request.method == 'POST':
        donation = session.get('donation', {})
        user_id = session.get('user_id')
        try:
            amount = float(donation.get('amount', 0))
        except (ValueError, TypeError):
            amount = 0.0
        description = "Card Payment"
        status = "completed"
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO payment_transactions (user_id, amount, description, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, description, status))
        conn.commit()
        conn.close()
        session.pop('donation', None)
        flash("Card payment processed successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('card_payment.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    """
    Admin Dashboard: Manage users, content, sightings, and announcements.
    """
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete_user':
            user_id = request.form.get('user_id')
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        elif action == 'update_user_role':
            user_id = request.form.get('user_id')
            new_role = request.form.get('role')
            role_id = conn.execute('SELECT id FROM user_roles WHERE role_name = ?', (new_role,)).fetchone()
            if role_id:
                conn.execute('UPDATE users SET role_id = ? WHERE id = ?', (role_id['id'], user_id))
        elif action == 'update_content':
            content_id = request.form.get('content_id')
            is_public = 1 if request.form.get('is_public') else 0
            conn.execute('UPDATE content_submissions SET is_public = ? WHERE id = ?', (is_public, content_id))
        elif action == 'delete_content':
            content_id = request.form.get('content_id')
            conn.execute('DELETE FROM content_submissions WHERE id = ?', (content_id,))
        elif action == 'delete_sighting':
            sighting_id = request.form.get('sighting_id')
            conn.execute('DELETE FROM wildlife_sightings WHERE id = ?', (sighting_id,))
        elif action == 'add_announcement':
            announcement = request.form.get('announcement')
            users = conn.execute('SELECT id FROM users').fetchall()
            for user in users:
                conn.execute('INSERT INTO notifications (user_id, content) VALUES (?, ?)', (user['id'], announcement))
        conn.commit()

    users = conn.execute('''
        SELECT users.id, username, email, role_name 
        FROM users
        JOIN user_roles ON users.role_id = user_roles.id
    ''').fetchall()

    contents = conn.execute('''
        SELECT cs.id, cs.title, cs.is_public, u.username 
        FROM content_submissions cs
        JOIN users u ON cs.user_id = u.id
    ''').fetchall()

    sightings = conn.execute('''
        SELECT ws.id, ws.species, ws.location, ws.timestamp, u.username as uploader
        FROM wildlife_sightings ws
        JOIN users u ON ws.user_id = u.id
        ORDER BY ws.timestamp DESC
    ''').fetchall()

    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_sightings': conn.execute('SELECT COUNT(*) FROM wildlife_sightings').fetchone()[0],
        'total_content': conn.execute('SELECT COUNT(*) FROM content_submissions').fetchone()[0],
        'total_payments': conn.execute('SELECT COUNT(*) FROM payment_transactions').fetchone()[0]
    }
    conn.close()
    return render_template('admin_dashboard.html', users=users, contents=contents, stats=stats, sightings=sightings)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/endangered_species')
def endangered_species():
    """
    Displays all endangered species (static + community-reported).
    """
    data = get_endangered_species_data()
    return render_template('endangered_species.html', static_species=data)

@app.route('/subscribe_newsletter', methods=['POST'])
def subscribe_newsletter():
    """
    Subscribes a user to the newsletter if not already subscribed.
    """
    email = request.form.get('email')
    if email:
        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM newsletter_subscribers WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("This email is already subscribed.", "info")
        else:
            conn.execute("INSERT INTO newsletter_subscribers (email) VALUES (?)", (email,))
            conn.commit()
            flash("Thank you for subscribing to our newsletter!", "success")
        conn.close()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """
    Renders a custom 404 page if a route is not found.
    """
    return render_template('404.html'), 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
