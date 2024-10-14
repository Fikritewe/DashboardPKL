import sqlite3

connection = sqlite3.connect("user_database.db")
cursor = connection.cursor()

cursor.execute("INSERT INTO users VALUES ('fikri@gmail.com', '12345678')")
cursor.execute("INSERT INTO users VALUES ('gale@gmail.com','password-gale')")
cursor.execute("INSERT INTO users VALUES ('kepin@gmail.com','112233')")

connection.commit()

