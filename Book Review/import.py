import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

engine.execute("DROP TABLE users CASCADE")
engine.execute("DROP TABLE books CASCADE")
engine.execute("DROP TABLE reviews CASCADE")

engine.execute(
        """CREATE TABLE users
                (
                    id SERIAL PRIMARY KEY,
                    uname VARCHAR UNIQUE,
                    email VARCHAR NOT NULL,
                    password VARCHAR NOT NULL
                )"""
            )

engine.execute(
        """CREATE TABLE books
                (
                    id SERIAL PRIMARY KEY,
                    isbn INT NOT NULL,
                    title VARCHAR NOT NULL,
                    author VARCHAR NOT NULL,
                    pyear INT NOT NULL
                )"""
            )

engine.execute(
        """CREATE TABLE reviews
                (
                    uid INT PRIMARY KEY,
                    comment VARCHAR,
                    isbn INT,
                    FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY(isbn) REFERENCES books(isbn) ON DELETE CASCADE
                )"""
            )

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author,pyear in reader:
        db.execute("INSERT INTO books (isbn, title, author,pyear) VALUES (:isbn, :title, :author,:pyear)",
                    {"isbn": isbn, "title": title, "author": author,"pyear":pyear})
        print(f"Added  {title} by {author} .")
    db.commit()

if __name__ == "__main__":
    main()
