from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# socketio library
from flask_socketio import SocketIO, send, emit, join_room, leave_room

# server library
import eventlet


eventlet.monkey_patch()

# build a web application by flask
app = Flask(__name__)
app.secret_key = 'asdfghjkl' 

# initialize SocketIO
socketio = SocketIO(app)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    page = int(request.args.get('page', 1))
    books_per_page = 6
    offset = (page - 1) * books_per_page

    search_query = request.args.get('search', '')

    conn = get_db_connection()

    user_id = session.get('user_id')
    user_gender = None
    user_age = None
    user_favorite_genre = None
    user_read_books = []

    if user_id:
        user_data = conn.execute('SELECT gender, age, favorite_genre, read_books FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_data:
            user_gender = user_data['gender']
            user_age = user_data['age']
            user_favorite_genre = user_data['favorite_genre']
            user_read_books = user_data['read_books'].split(',') if user_data['read_books'] else []


    read_books_genres_authors_query = '''
        SELECT DISTINCT genre, author FROM books WHERE title IN ({seq})
    '''
    placeholders = ', '.join(['?'] * len(user_read_books)) if user_read_books else 'NULL'
    formatted_read_books_genres_authors_query = read_books_genres_authors_query.format(seq=placeholders)
    read_books_genres_authors = {row[0]: row[1] for row in conn.execute(formatted_read_books_genres_authors_query, user_read_books).fetchall()}

    query = '''
        SELECT books.*, 
               IFNULL(SUM(reviews.like_count), 0) AS total_likes,
               CASE 
                   WHEN books.genre = ? THEN 0  
                   WHEN books.author IN ({author_seq}) THEN 1  
                   WHEN books.genre IN ({genre_seq}) AND books.genre != ? THEN 2  
                   WHEN (? IS NOT NULL AND ? IS NOT NULL AND users.gender = ? AND users.age BETWEEN ? AND ?) THEN 3
                   ELSE 4
               END AS priority
        FROM books
        LEFT JOIN reviews ON books.id = reviews.book_id
        LEFT JOIN users ON reviews.user_id = users.id
        WHERE (books.title LIKE ? OR books.author LIKE ? OR books.description LIKE ?)
        GROUP BY books.id
        ORDER BY priority ASC, total_likes DESC
        LIMIT ? OFFSET ?
    '''

    # dynamically create placeholders for the IN clause based on the number of read_books genres and authors
    read_books_genres_placeholders = ', '.join(['?'] * len(read_books_genres_authors.keys())) if read_books_genres_authors else 'NULL'
    read_books_authors_placeholders = ', '.join(['?'] * len(set(read_books_genres_authors.values()))) if read_books_genres_authors else 'NULL'
    formatted_query = query.format(
        author_seq=read_books_authors_placeholders,
        genre_seq=read_books_genres_placeholders
    )

    search_term = f"%{search_query}%"

    # prepare query parameters
    query_params = [
        user_favorite_genre,
        *list(set(read_books_genres_authors.values())),  # 已读书籍的作者
        *list(read_books_genres_authors.keys()),         # 已读书籍的类型
        user_favorite_genre,
        user_gender, user_age, user_gender, user_age - 5 if user_age else 0, user_age + 5 if user_age else 0,
        search_term, search_term, search_term,
        books_per_page, offset
    ]

    try:
        books = conn.execute(formatted_query, query_params).fetchall()
        if not books:
            flash('No books found matching your search query.', 'info')

        total_books_query = '''
            SELECT COUNT(*)
            FROM books
            WHERE (books.title LIKE ? OR books.author LIKE ? OR books.description LIKE ?)
        '''
        total_books = conn.execute(total_books_query, query_params[-7:-4]).fetchone()[0]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        books = []
        total_books = 0

    conn.close()

    total_pages = (total_books + books_per_page - 1) // books_per_page

    return render_template(
        'index.html',
        books=books,
        page=page,
        total_pages=total_pages,
        search_query=search_query
    )


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_template('chat.html')


@socketio.on('message')
def handle_message(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)


@socketio.event
def joinRoom(message):
    username = session.get('username')

    #print(message)
    join_room(message['room'])

    emit("roomJoined", {
        "user": username,
        "room": message['room']
    }, to=message['room'])


@socketio.event
def leaveRoom(message):
    username = session.get('username')

    # emit to the user that they have left the room
    emit('roomLeftPersonal', {
        'user': username,
        'room': message['room']
        })
    
    leave_room(message['room'])

    # emit to the room that the user has left
    emit('roomLeft', {
        'user': username,
        'room': message['room']
    }, to=message['room'])


@socketio.event
def sendMsg(message):
    username = session.get('username')

    emit('sendToAll', {
        'msg': message['msg'],
        'user': username
    }, to = message['room'])


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book(book_id):
    conn = get_db_connection()

    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()

    user_id = session.get('user_id')
    reviews = conn.execute('''
        SELECT reviews.*, 
               (SELECT COUNT(*) FROM user_likes WHERE review_id = reviews.id) AS like_count,
               EXISTS (SELECT 1 FROM user_likes WHERE review_id = reviews.id AND user_id = ?) AS liked_by_user
        FROM reviews
        WHERE reviews.book_id = ?
    ''', (user_id, book_id)).fetchall()


    if request.method == 'POST':
        if 'content' in request.form:
            content = request.form['content']
            user_id = session.get('user_id')
            if user_id:
                conn.execute('INSERT INTO reviews (book_id, user_id, content) VALUES (?, ?, ?)',
                             (book_id, user_id, content))
                conn.commit()
                flash('You have submitted a Like!', 'success')
            else:
                flash('Please log in and submit Like', 'danger')

            return redirect(url_for('book', book_id=book_id))

    conn.close()
    return render_template('book.html', book=book, reviews=reviews)


@app.route('/like_comment/<int:review_id>', methods=['POST'])
def like_comment(review_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User name does not exist"}), 400

    conn = get_db_connection()

    review = conn.execute('SELECT * FROM reviews WHERE id = ?', (review_id,)).fetchone()
    if not review:
        return jsonify({"error": "No Reviews available"}), 404

    if review['user_id'] == user_id:
        return jsonify({"error": "The review submitted by oneself cannot be liked"}), 400

    existing_like = conn.execute(
        'SELECT * FROM user_likes WHERE user_id = ? AND review_id = ?',
        (user_id, review_id)
    ).fetchone()
    if existing_like:
        return jsonify({"error": "You have already liked it"}), 400

    conn.execute('UPDATE reviews SET like_count = like_count + 1 WHERE id = ?', (review_id,))
    conn.commit()

    conn.execute('INSERT INTO user_likes (user_id, review_id) VALUES (?, ?)', (user_id, review_id))
    conn.commit()

    like_count = conn.execute('SELECT like_count FROM reviews WHERE id = ?', (review_id,)).fetchone()['like_count']

    conn.close()

    return jsonify({'new_like_count': like_count})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            if user['is_admin']:
                return redirect(url_for('users'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        age = request.form['age']
        gender = request.form['gender']
        favorite_genre = request.form['favorite_genre']

        # Collect all selected books and join them into a single string separated by commas
        read_books_list = request.form.getlist('read_books')
        read_books_str = ','.join(read_books_list) if read_books_list else ''

        conn = get_db_connection()
        try:
            conn.execute('''
            INSERT INTO users (username, password, age, gender, favorite_genre, read_books) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password, age, gender, favorite_genre, read_books_str))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return 'The username already exists'
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    reviews = conn.execute('SELECT * FROM reviews WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return render_template('profile.html', user=user, reviews=reviews)


@app.route('/users')
def users():
    if 'user_id' not in session:
        print("user_id not in session")
        flash('Access Denied: User not logged in.', 'danger')
        return redirect(url_for('index'))
    
    if not session.get('is_admin', False):
        print("User is not an admin")
        flash('Access Denied: You are not authorized to view this page.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    non_admin_users = conn.execute('SELECT * FROM users WHERE is_admin = 0').fetchall()
    conn.close()
    return render_template('admin_users.html', users=[dict(user) for user in non_admin_users])
 

if __name__ == '__main__':
    socketio.run(app, debug=True)
