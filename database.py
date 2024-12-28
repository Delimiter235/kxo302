import sqlite3

# init db
conn = sqlite3.connect('database.db')
c = conn.cursor()


# users
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    gender TEXT,
    age Integer,
    favorite_genre TEXT,
    is_admin INTEGER DEFAULT 0 ,
    read_books TEXT DEFAULT '' 
)

''')

c.execute('''
INSERT INTO users (username, password, gender,age,favorite_genre,is_admin,read_books)
VALUES (?,?,?,?,?,?,?)
''',
('admin', 'scrypt:32768:8:1$ce00gtRdFxOC3D6t$342549dfd6cc81b0c8e858b5a73c74f57952998465ba7e706ae3088b062db8b27eaea2201a4240e4597a09e564bdbaace10cd583292df3997de62e13307ab26b','male',30,'Fiction',1,''))

# books
c.execute('''
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    description TEXT,
    url TEXT
)
''')

# reviews
c.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    content TEXT,
    like_count INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
)
''')

# user_likes 
c.execute('''
CREATE TABLE IF NOT EXISTS user_likes (
    user_id INTEGER NOT NULL,
    review_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, review_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (review_id) REFERENCES reviews(id)
)
''')


# init book
data = [
    ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 'A novel set in the Jazz Age that critiques the American Dream.','image/1.jpg'),
    ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 'A story of racial injustice in the Deep South during the 1930s.','image/2.jpg'),
    ('1984', 'George Orwell', 'Dystopian', 'A novel about a totalitarian regime that uses surveillance to control its citizens.','image/3.jpg'),
    ('Pride and Prejudice', 'Jane Austen', 'Romance', 'A love story that explores the themes of social class and relationships.','image/4.jpg'),
    ('Moby-Dick', 'Herman Melville', 'Adventure', 'The story of Captain Ahab’s obsession with the white whale, Moby Dick.','image/5.jpg'),
    ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 'A story about teenage rebellion and the struggles of growing up.','image/6.jpg'),
    ('Brave New World', 'Aldous Huxley', 'Dystopian', 'A dystopian novel that explores a future society controlled by technology and consumerism.','image/7.jpg'),
    ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 'The prequel to The Lord of the Rings, telling the adventure of Bilbo Baggins.','image/8.jpg'),
    ('Fahrenheit 451', 'Ray Bradbury', 'Dystopian', 'A novel set in a future society where books are banned and burned.','image/9.jpg'),
    ('The Lord of the Rings: The Fellowship of the Ring', 'J.R.R. Tolkien', 'Fantasy', 'The first part of the epic tale of the One Ring and the battle between good and evil.','image/10.jpg'),
    ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', 'Fantasy', 'The beginning of Harry Potter\'s journey to defeat dark forces in a magical world.','image/11.jpg'),
    ('The Alchemist', 'Paulo Coelho', 'Fiction', 'A story about a shepherd named Santiago who searches for his personal legend.','image/12.jpg'),
    ('Crime and Punishment', 'Fyodor Dostoevsky', 'Classic', 'A psychological drama about morality, redemption, and guilt.','image/13.jpg'),
    ('The Grapes of Wrath', 'John Steinbeck', 'Fiction', 'The struggles of a poor family during the Great Depression as they seek a better life.','image/14.jpg'),
    ('Jane Eyre', 'Charlotte Brontë', 'Romance', 'The story of an orphaned girl who becomes a governess and finds love and independence.','image/15.jpg'),
    ('Wuthering Heights', 'Emily Brontë', 'Gothic', 'A tale of passion, revenge, and the haunting effects of unrequited love.','image/16.jpg'),
    ('The Picture of Dorian Gray', 'Oscar Wilde', 'Classic', 'A man remains eternally youthful while his portrait ages, reflecting his inner corruption.','image/17.jpg'),
    ('Anna Karenina', 'Leo Tolstoy', 'Classic', 'A tragic story of love, betrayal, and societal pressures in Imperial Russia.','image/18.jpg'),
    ('The Road', 'Cormac McCarthy', 'Post-Apocalyptic', 'A father and son journey through a bleak and desolate world in search of survival.','image/19.jpg'),
    ('One Hundred Years of Solitude', 'Gabriel García Márquez', 'Magical Realism', 'The multi-generational tale of the Buendía family in the fictional town of Macondo.','image/20.jpg'),
    ('Frankenstein', 'Mary Shelley', 'Gothic', 'The story of a scientist who creates a monster and faces the consequences of playing god.','image/21.jpg'),
    ('Les Misérables', 'Victor Hugo', 'Historical Fiction', 'A tale of justice, redemption, and love set during 19th century France.','image/22.jpg'),
    ('The Divine Comedy', 'Dante Alighieri', 'Classic', 'A journey through Hell, Purgatory, and Paradise guided by allegorical symbolism.','image/23.jpg'),
    ('The Count of Monte Cristo', 'Alexandre Dumas', 'Adventure', 'A story of betrayal, revenge, and justice following the imprisonment of Edmond Dantès.','image/24.jpg'),
    ('Don Quixote', 'Miguel de Cervantes', 'Classic', 'The adventures of a nobleman who imagines himself a knight on a quest for chivalry.','image/25.jpg'),
    ('Dracula', 'Bram Stoker', 'Horror', 'The classic story of Count Dracula, a vampire who preys on the living.','image/26.jpg'),
    ('The Odyssey', 'Homer', 'Epic', 'The epic tale of Odysseus’ ten-year journey home after the Trojan War.','image/27.jpg'),
    ('The Kite Runner', 'Khaled Hosseini', 'Historical Fiction', 'A story of friendship, betrayal, and redemption set in Afghanistan.','image/28.jpg'),
    ('Life of Pi', 'Yann Martel', 'Adventure', 'The survival story of a boy stranded on a lifeboat with a Bengal tiger.','image/29.jpg'),
    ('A Tale of Two Cities', 'Charles Dickens', 'Historical Fiction', 'A novel set during the French Revolution exploring sacrifice and redemption.','image/30.jpg'),
    ('The Bell Jar', 'Sylvia Plath', 'Fiction', 'A semi-autobiographical story about mental illness and societal pressures.','image/31.jpg'),
    ('The Shining', 'Stephen King', 'Horror', 'The terrifying story of a family isolated in a haunted hotel during the winter.','image/32.jpg'),
    ('The Giver', 'Lois Lowry', 'Dystopian', 'A story about a boy who discovers the dark truth behind his seemingly perfect society.','image/33.jpg'),
    ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Mystery', 'A journalist and a hacker uncover secrets surrounding a decades-old disappearance.','image/34.jpg'),
    ('The Hunger Games', 'Suzanne Collins', 'Dystopian', 'A girl fights for survival in a televised death match in a post-apocalyptic world.','image/35.jpg')
]

# 批量插入数据
c.executemany('''
INSERT INTO books (title, author, genre, description,url) VALUES (?, ?, ?, ?,?)
''', data)


conn.commit()
conn.close()
