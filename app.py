from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from config import Config
import os

# Get the absolute path to the project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Initialize Flask with explicit paths
app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)
app.secret_key = Config.SECRET_KEY

# Session configuration for production (PythonAnywhere)
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True if using HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)

def get_db_connection():
    """Get SQLite database connection"""
    try:
        connection = sqlite3.connect(Config.DB_PATH)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        raise

def init_db():
    """Initialize the database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def test_db_connection():
    """Test database connection on startup"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("1. SQLite database path is accessible")
        print("2. You have write permissions in the project directory")
        return False

def verify_project_structure():
    """Verify that all required directories exist"""
    print(f"\n📁 Project Directory: {BASE_DIR}")
    print(f"📁 Templates Directory: {TEMPLATE_DIR}")
    print(f"📁 Static Directory: {STATIC_DIR}")

    if not os.path.exists(TEMPLATE_DIR):
        print(f"❌ Templates folder not found at: {TEMPLATE_DIR}")
        print("   Please create the 'templates' folder")
        return False

    if not os.path.exists(STATIC_DIR):
        print(f"❌ Static folder not found at: {STATIC_DIR}")
        print("   Please create the 'static' folder")
        return False

    # Check for required template files
    required_templates = ['landing.html', 'question.html', 'message.html', 'thank_you.html']
    missing_templates = []

    for template in required_templates:
        template_path = os.path.join(TEMPLATE_DIR, template)
        if os.path.exists(template_path):
            print(f"✅ Found: templates/{template}")
        else:
            print(f"❌ Missing: templates/{template}")
            missing_templates.append(template)

    # Check for static folders
    css_dir = os.path.join(STATIC_DIR, 'css')
    js_dir = os.path.join(STATIC_DIR, 'js')

    if os.path.exists(css_dir):
        print(f"✅ Found: static/css/")
    else:
        print(f"❌ Missing: static/css/")
        os.makedirs(css_dir, exist_ok=True)
        print(f"✅ Created: static/css/")

    if os.path.exists(js_dir):
        print(f"✅ Found: static/js/")
    else:
        print(f"❌ Missing: static/js/")
        os.makedirs(js_dir, exist_ok=True)
        print(f"✅ Created: static/js/")

    if missing_templates:
        print(f"\n⚠️  Missing templates: {', '.join(missing_templates)}")
        return False

    return True

@app.route('/')
def landing():
    """Landing page with name input"""
    return render_template('landing.html')

@app.route('/submit-name', methods=['POST'])
def submit_name():
    """Handle name submission and store in database"""
    name = request.form.get('name', '').strip()

    if not name:
        return redirect(url_for('landing'))

    try:
        # Store name in database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        user_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        # Store user info in session
        session['user_id'] = user_id
        session['name'] = name

        return redirect(url_for('question'))

    except Exception as e:
        print(f"Error saving name: {e}")
        return redirect(url_for('landing'))

@app.route('/question')
def question():
    """The Valentine's question page"""
    if 'name' not in session:
        return redirect(url_for('landing'))

    return render_template('question.html', name=session['name'])

@app.route('/accept', methods=['POST'])
def accept():
    """Handle 'Yes' button click"""
    if 'user_id' not in session:
        return redirect(url_for('landing'))

    return redirect(url_for('message'))

@app.route('/message')
def message():
    """Message page for user response"""
    if 'name' not in session:
        return redirect(url_for('landing'))

    return render_template('message.html', name=session['name'])

@app.route('/submit-message', methods=['POST'])
def submit_message():
    """Handle message submission"""
    if 'user_id' not in session:
        return redirect(url_for('landing'))

    user_message = request.form.get('message', '').strip()

    if user_message:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO messages (user_id, message) VALUES (?, ?)',
                (session['user_id'], user_message)
            )

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error saving message: {e}")

    return render_template('thank_you.html', name=session['name'])

@app.route('/admin/view-data')
def view_data():
    """Admin route to view stored data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all users
        cursor.execute('SELECT * FROM users ORDER BY timestamp DESC')
        users = cursor.fetchall()

        # Get all messages with user names
        cursor.execute('''
            SELECT m.*, u.name 
            FROM messages m 
            JOIN users u ON m.user_id = u.id 
            ORDER BY m.timestamp DESC
        ''')
        messages = cursor.fetchall()

        cursor.close()
        conn.close()

        # Build HTML response
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin - View Data</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                h1 { color: #e91e63; }
                h2 { color: #333; margin-top: 30px; }
                table {
                    width: 100%;
                    background: white;
                    border-collapse: collapse;
                    margin: 20px 0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background: #e91e63;
                    color: white;
                }
                tr:hover {
                    background: #f5f5f5;
                }
                .count {
                    background: #e91e63;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 20px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>💕 Valentine's Day Admin Panel</h1>
        '''

        html += f'<h2>👥 Users <span class="count">{len(users)}</span></h2>'
        if users:
            html += '''
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Timestamp</th>
                </tr>
            '''
            for user in users:
                html += f'''
                <tr>
                    <td>{user["id"]}</td>
                    <td>{user["name"]}</td>
                    <td>{user["timestamp"]}</td>
                </tr>
                '''
            html += '</table>'
        else:
            html += '<p>No users yet.</p>'

        html += f'<h2>💌 Messages <span class="count">{len(messages)}</span></h2>'
        if messages:
            html += '''
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Message</th>
                    <th>Timestamp</th>
                </tr>
            '''
            for msg in messages:
                html += f'''
                <tr>
                    <td>{msg["id"]}</td>
                    <td><strong>{msg["name"]}</strong></td>
                    <td>{msg["message"]}</td>
                    <td>{msg["timestamp"]}</td>
                </tr>
                '''
            html += '</table>'
        else:
            html += '<p>No messages yet.</p>'

        html += '''
            <p style="margin-top: 40px;">
                <a href="/" style="color: #e91e63; text-decoration: none; font-weight: bold;">← Back to Home</a>
            </p>
        </body>
        </html>
        '''

        return html

    except Exception as e:
        return f'''
        <h1>Error</h1>
        <p>Could not retrieve data: {str(e)}</p>
        <p>Make sure your database is set up correctly.</p>
        '''

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Valentine's Day Website...")
    print("=" * 60)

    # Initialize database
    init_db()

    # Verify project structure
    if not verify_project_structure():
        print("\n⚠️  Please fix the project structure issues above.")
        input("\nPress Enter to exit...")
        exit(1)

    print("\n" + "=" * 60)

    # Test database connection
    if test_db_connection():
        print("=" * 60)
        print("✨ Server starting on http://localhost:5000")
        print("=" * 60)
        print("\n💡 Access the website at: http://localhost:5000")
        print("💡 View admin panel at: http://localhost:5000/admin/view-data")
        print("\n⚠️  Press CTRL+C to stop the server\n")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("\n⚠️  Please fix database connection issues before starting the server.")
        input("\nPress Enter to exit...")