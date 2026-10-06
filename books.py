import sqlite3
import unicodedata
import psycopg
import re

# import logging

# logging.basicConfig(
#     filename="debug.log",
#     level=logging.DEBUG,
#     format="%(asctime)s - %(message)s"
# )

class Database():
    def __init__(self, url):
        self.connection = psycopg.connect(url)
        self.db = self.connection.cursor()
        self.cacheDB = lambda:self.cacheDB_conn().cursor()
        self.bookList = lambda db, info, where="", params=(): db.execute(f"SELECT {",".join(info.split(" "))} FROM bibliotheque {where}", params)
        self.bookTitle = lambda bookName: f"\033[4m{bookName}\033[0m"

    def cacheDB_conn(self):
        conn = sqlite3.connect("cacheDB.db")
        conn.create_function("normalize", 1, lambda text:
            unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode().lower()
            if text else ""
        )
        return conn

    def initializeCache(self):
        books = self.bookList(self.db, "*").fetchall()
        cacheDB_conn = self.cacheDB_conn()
        cacheDB = cacheDB_conn.cursor()
        cacheDB.execute("DELETE FROM bibliotheque")
        for book in books:
            cacheDB.execute("INSERT INTO bibliotheque (id, title, author, gender, read, readed_at) VALUES (?, ?, ?, ?, ?, ?)", book)
        cacheDB_conn.commit()
        cacheDB_conn.close()


    def newBook(self, bookAuthor, bookName, bookGender, isRead):
        books = self.bookList(self.cacheDB(), "title author").fetchall()
        if (bookName, bookAuthor) in books:
            return True
        else:
            self.bookList(self.db, "*").execute("INSERT INTO bibliotheque (title, author, gender, read) VALUES (%s, %s, %s, %s)", (bookName, bookAuthor, bookGender.title(), isRead))
            self.connection.commit()
            self.initializeCache()


    def modifyBook(self, bookName, bookAuthor, bookGender, bookRead, bookID):
        self.bookList(self.db, "*").execute("UPDATE bibliotheque SET title = %s, author = %s, gender = %s, read = %s WHERE id = %s", (bookName, bookAuthor, bookGender, bookRead, int(bookID)))
        self.connection.commit()
        self.initializeCache()


    def deleteBook(self, bookID):
        self.db.execute("DELETE FROM bibliotheque WHERE id = %s", (bookID,))
        self.connection.commit()
        self.initializeCache()


    def listBook(self, inputChain): # return books
        if inputChain != "":
            conditions = []
            params = []

            inputChain = re.split(r"(@a|@t|@g|@rr|@r)", inputChain)
            inputAuthor = inputChain[inputChain.index("@a") + 1].strip() if "@a" in inputChain else ""
            inputTitle = inputChain[inputChain.index("@t") + 1].strip() if "@t" in inputChain else ""
            inputGender = inputChain[inputChain.index("@g") + 1].strip() if "@g" in inputChain else ""
            inputRead = True if "@r" in inputChain else False if "@rr" in inputChain else None

            if inputAuthor:
                conditions.append("normalize(author) LIKE normalize(?)")
                params.append(f"%{inputAuthor}%")
            if inputTitle:
                conditions.append("normalize(title) LIKE normalize(?)")
                params.append(f"%{inputTitle}%")
            if inputGender:
                conditions.append("normalize(gender) LIKE normalize(?)") 
                params.append(f"%{inputGender}%")
            if inputRead:
                conditions.append("read = ?")
                params.append(True)
            elif inputRead == False:
                conditions.append("read = ?")
                params.append(False)

            if conditions:
                where = "WHERE " + " AND ".join(conditions)
            else:
                where = "WHERE normalize(title) LIKE normalize(?) or normalize(author) LIKE normalize(?)"
                params = [f"%{inputChain[0]}%", f"%{inputChain[0]}%"]

            books = self.bookList(self.cacheDB(), "id title author gender read", where, tuple(params)).fetchall()

        else:
            books = self.bookList(self.cacheDB(), "id title author gender read").fetchall()

        nbrOfBooks = len(books)
        nbrReadBooks = 0
        for book in books:
            if book[4]:
                nbrReadBooks += 1 
        books = sorted(books, key=lambda book: (unicodedata.normalize("NFD", book[2].split(" ")[-1]).encode("ascii", "ignore").decode().casefold(),unicodedata.normalize("NFD", book[1]).encode("ascii", "ignore").decode().casefold()))
        return (books, nbrOfBooks, nbrReadBooks)


    def putBook(self):
        bookName, bookAuthor = self.chooseBook(False)
        if (bookName, bookAuthor) not in self.bookList("title author").fetchall():
            print("Le livre n'est pas dans la bibliothèque !")
            if input("Voulez vous en ranger un autre ? (oui/non) ").lower() == "oui":
                self.putBook()
            return
        book = self.bookList("title author gender", "WHERE title = %s AND author = %s", (bookName, bookAuthor)).fetchall()[0]
        books = self.bookList("title author gender", "WHERE gender = %s", (book[2],)).fetchall()
        books = sorted(books, key = lambda book : (book[1].split(" ")[-1], book[0]))

        bookIndex = books.index(book)
        if bookIndex == 0:
            preBook = 0
        else:
            preBook = books[bookIndex - 1]

        if bookIndex == len(books) - 1:
            postBook = 0
        else:
            postBook = books[bookIndex + 1]

        if preBook == 0:
            print(f"C'est le premier livre à mettre en {book[2].title()} ! Le livre après est {self.bookTitle(postBook[0])} de {postBook[1]}")
        elif postBook == 0:
            print(f"C'est le dernier livre à mettre en {book[2].title()} ! Le livre avant est {self.bookTitle(preBook[0])} de {preBook[1]}")
        else:
            if preBook[1] == postBook[1]:
                print(f"Il faut ranger {self.bookTitle(book[0])} entre {self.bookTitle(preBook[0])} et {self.bookTitle(postBook[0])} de {book[1]}")
            else:
                print(f"Il faut ranger {self.bookTitle(book[0])} de {book[1]} entre {self.bookTitle(preBook[0])} de {preBook[1]} et {self.bookTitle(postBook[0])} de {postBook[1]}")

