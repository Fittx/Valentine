from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from psycopg2.extras import RealDictCursor
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

# Session configuration for production

# Session configuration for production
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Render uses HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    # Removed SESSION_TYPE - Flask will use signed cookies by default
)

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        connection = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursor_factory=RealDictCursor
        )
        connection.autocommit = False
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise


def init_db():
    """Initialize the database with tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           name
                           VARCHAR
                       (
                           255
                       ) NOT NULL,
                           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           )
                       ''')

        # Create messages table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS messages
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           message
                           TEXT
                           NOT
                           NULL,
                           timestamp
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       )
                           )
                       ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database tables initialized!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

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
        print("1. PostgreSQL is running")
        print("2. Database credentials are correct")
        print("3. Database exists")
        return False




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

        cursor.execute('INSERT INTO users (name) VALUES (%s) RETURNING id', (name,))
        user_id = cursor.fetchone()['id']

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
                'INSERT INTO messages (user_id, message) VALUES (%s, %s)',
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
        # Removed input() for production
        exit(1)

    print("\n" + "=" * 60)

    # Test database connection
    if test_db_connection():
        print("=" * 60)
        print("✨ Server starting...")
        print("=" * 60)

        # Use environment variable PORT for Render
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        print("\n⚠️  Please fix database connection issues before starting the server.")
        # Removed input() for production
        exit(1)