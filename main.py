import psycopg
import os

connection = psycopg.connect("connect link (like postgresql://neondv_owner;hfjdskfhjksdfhkjsd@hfjdskhfjkdshfkjsd...")
import psycopg
import os

connection = psycopg.connect("postgresql://neondb_owner:npg_g9qlrvEtx8zb@ep-fragrant-recipe-b1r7tfr2-pooler.c-5.eu-central-1.aws.neon.tech/bibliotheque?sslmode=require&channel_binding=require")
db = connection.cursor()

bookList = lambda info, where="", params=(): db.execute(f"SELECT {",".join(info.split(" "))} FROM bibliotheque {where}", params)
bookTitle = lambda bookName: f"\033[4m{bookName}\033[0m"

def chooseBook(gender):
    bookName = input("\nQuel est le nom du livre ? ")
    bookAuthor = input("Quel est le nom de l'auteur ? ")
    if gender:
        bookGender = input("Quel est le genre du livre ? ").title()
    while True:
        choice = input(f"Le livre est bien '{bookName}' par {bookAuthor} ? (oui/non) ").lower()
        if choice == "non":
            if gender:
                error = input("Qu'est ce qui est érroné, le nom du livre (1), le nom de l'auteur (2) ou le genre (3) ? ")
            else:
                error = input("Qu'est ce qui est érroné, le nom du livre (1) ou le nom de l'auteur (2) ? ")
            if error == "1":
                bookName = input("Quel est le nom du livre ? ")
            elif error == "2":
                bookAuthor = input("Quel est le nom de l'auteur ? ")
            elif (error == "3") and (gender) :
                bookGender = input("Quel est le genre du livre ? ").title()
            else:
                print("Veuillez choisir une option valide !")
        elif choice == "oui":
            break
        else:
            print("Veuillez choisir une option valide !")

    if gender:
        return (bookName.strip(), bookAuthor.strip(), bookGender.strip())
    else: 
        return (bookName.strip(), bookAuthor.strip())


def newBook():
    bookName, bookAuthor, bookGender = chooseBook(True)
    books = bookList("title author").fetchall()
    if (bookName, bookAuthor) in books:
        print("Le livre est déjà dans la bibliothèque !")
        if input("Voulez vous en ajouter un autre ? (oui/non) ").lower() == "oui":
            return newBook()
    else:
        isRead = input("Avez vous lu le livre ? (oui/non) ").lower() == "oui"
        bookList("*").execute("INSERT INTO bibliotheque (title, author, gender, read) VALUES (%s, %s, %s, %s)", (bookName, bookAuthor, bookGender.title(), isRead))
        connection.commit()


def modifyBook():
    books = bookList("title author").fetchall()
    bookName, bookAuthor = chooseBook(False)
    if (bookName, bookAuthor) not in books:
        print("Le livre n'est pas dans la bibliothèque !")
        if input("Voulez vous en modifier un autre ? (oui/non) ").lower() == "oui":
            modifyBook()
    else:
        book = bookList("title author gender read", "WHERE title = %s AND author = %s", (bookName, bookAuthor)).fetchall()
        book = list(book[0])
        while True:
            choice = input(f"Que voulez vous modifier sur {bookTitle(book[0])}, {book[1]},  {book[2]}, {"lu" if book[3] else "pas lu"} ? (Nom, Auteur, Genre, Lu, Supprimer) ?\nChoix: ").lower()

            if choice == "nom":
                newName = input(f"Quel nouveau nom voulez vous donner à {bookTitle(book[0])} de {book[1]} ? ")
                book[0] = newName
                db.execute("UPDATE bibliotheque SET title = %s WHERE title = %s AND author = %s", (newName, bookName, bookAuthor))
            elif choice == "auteur":
                newAuthor = input(f"Quel est le nouveau nom de l'auteur de {bookTitle(book[0])} de {book[1]} ? ")
                book[1] = newAuthor
                db.execute("UPDATE bibliotheque SET author = %s WHERE title = %s AND author = %s", (newAuthor, bookName, bookAuthor))
            elif choice == "genre":
                newGender = input(f"Quel est le nouveau nom de l'auteur de {bookTitle(book[0])} de {book[1]}, {book[2]} ? ")
                book[2] = newGender
                db.execute("UPDATE bibliotheque SET gender = %s WHERE title = %s AND author = %s", (newGender, bookName, bookAuthor))
            elif choice == "lu":
                book[3] = not book[3]
                db.execute("UPDATE bibliotheque SET read = %s WHERE title = %s AND author = %s", (book[3], bookName, bookAuthor))
                print(f"Le livre est bien noté en {"lu" if book[3] else "non lu"}")
            elif choice == "supprimer":
                delete = input(f"Etes vous sûr de vouloir supprimer {bookTitle(book[0])} de {book[1]} ? (oui/non) ").lower() == "oui"
                if delete:
                    db.execute("DELETE FROM bibliotheque WHERE title = %s AND author = %s", (bookName, bookAuthor))
                    connection.commit()
                    return
            else:
                print("Veuillez choisir une option valide !")
                continue

            connection.commit()
            choice = input("Voulez vous modifier quelque chose d'autre sur le livre ? (oui/non) ").lower()
            if choice == "non":
                break


def listBook():
    nbrOfBooks = len(bookList("read").fetchall())
    nbrReadBooks = len(bookList("read", "WHERE read = %s", (True,)).fetchall())
    print(f"\nVous avez lu {nbrReadBooks}/{nbrOfBooks} livres soit {(100 * nbrReadBooks / nbrOfBooks if nbrOfBooks else 0):.1f}% de votre bibliothèque.")
    choice = input("Vous voulez:\n1. Lister tout les livres\n2. Lister les livres par genre\n3. Lister les livres lus\n4. Lister les livres non lus\nChoix: ")
    books = bookList("title author gender read")
    while True: 
        if choice == "1":
            books = bookList("title author gender read").fetchall()
            break
        elif choice == "2":
            genderChoice = input("Quel genre de livre voulez vous voir ? ").title()
            genders = [i[0] for i in db.execute("SELECT DISTINCT gender FROM bibliotheque").fetchall()]
            while genderChoice not in genders:
                genderChoice = input("Ce type de genre n'est pas présent, quel genre de livre voulez vous voir ? ")
            books = bookList("title author gender read", "WHERE gender = %s", (genderChoice,)).fetchall()
            nbrOfBooks = len(books)
            nbrReadBooks = len(bookList("read gender", "WHERE read = %s AND gender = %s", (True, genderChoice)).fetchall())
            print(f"Vous avez lu {nbrReadBooks}/{nbrOfBooks} livres de {genderChoice.lower()} soit {(100 * nbrReadBooks / nbrOfBooks if nbrOfBooks else 0):.1f}% de votre bibliothèque.")
            break
        elif choice == "3":
            books = bookList("title author gender read", "WHERE read = %s", (True,)).fetchall()
            break
        elif choice == "4":
            books = bookList("title author gender read", "WHERE read = %s", (False,)).fetchall()
            break
        else:
            print("Veuillez choisir une option valide !")

    print("\nVous avez:")
    books = sorted(books, key = lambda book : (book[1].split(" ")[-1], book[0]))
    for book in books:
        print(f"{bookTitle(book[0])}, {book[1]}, {book[2]}, {"lu" if book[3] else "pas lu"}")


def putBook():
    bookName, bookAuthor = chooseBook(False)
    if (bookName, bookAuthor) not in bookList("title author").fetchall():
        print("Le livre n'est pas dans la bibliothèque !")
        if input("Voulez vous en ranger un autre ? (oui/non) ").lower() == "oui":
            putBook()
        return
    book = bookList("title author gender", "WHERE title = %s AND author = %s", (bookName, bookAuthor)).fetchall()[0]
    books = bookList("title author gender", "WHERE gender = %s", (book[2],)).fetchall()
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
        print(f"C'est le premier livre à mettre en {book[2].title()} ! Le livre après est {bookTitle(postBook[0])} de {postBook[1]}")
    elif postBook == 0:
        print(f"C'est le dernier livre à mettre en {book[2].title()} ! Le livre avant est {bookTitle(preBook[0])} de {preBook[1]}")
    else:
        if preBook[1] == postBook[1]:
            print(f"Il faut ranger {bookTitle(book[0])} entre {bookTitle(preBook[0])} et {bookTitle(postBook[0])} de {book[1]}")
        else:
            print(f"Il faut ranger {bookTitle(book[0])} de {book[1]} entre {bookTitle(preBook[0])} de {preBook[1]} et {bookTitle(postBook[0])} de {postBook[1]}")


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[H\033[J", end="")


def menu():
    choice = input("\nQue voulez vous faire ?\n1. Ajouter un livre dans la bibliothèque\n2. Ranger un livre\n3. Lister les livres\n4. Modifier un livre\n5. Supprimer les espaces en trop (espaces de début et de fin)\n6. Vider le terminal\n7. Quitter le programme\nChoix: ").lower()

    if not choice.isdigit():
        print("Veuillez choisir une option valide !")
        return menu()
    else:
        choice = int(choice)

    if choice == 1:
        newBook()
    elif choice == 2:
        putBook()
    elif choice == 3:
        listBook()
    elif choice == 4:
        modifyBook()
    elif choice == 5:
        db.execute("UPDATE bibliotheque SET title = TRIM(title),author = TRIM(author),gender = TRIM(gender);")
        connection.commit()
    elif choice == 6:
        clear()
    elif choice == 7:
        exit()
    else:
        print("Veuillez choisir une option valide !")
        return menu()


while True:
    menu()
