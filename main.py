import os
from supabase import create_client

supabase = create_client(
    "PROJECT_URL (like https://jfdskljfklsdjfklsdjfklsdjfl.supabase.co)",
    "PUBLISHABLE_KEY (like sb_publishable_fhdjkfhksdjhfkjs_hfdjsfhsdjk)"
)

bookList = lambda: supabase.table("bibliotheque")
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
        return (bookName, bookAuthor, bookGender)
    else: 
        return (bookName, bookAuthor)
    
    
def newBook():
    bookName, bookAuthor, bookGender = chooseBook(True)
    books = bookList().select("title", "author").execute().data
    if {'title': bookName, 'author': bookAuthor} in books:
        print("Le livre est déjà dans la bibliothèque !")
        if input("Voulez vous en ajouter un autre ? (oui/non) ").lower() == "oui":
            return newBook()
    else:
        isRead = input("Avez vous lu le livre ? (oui/non) ").lower() == "oui"
        bookList().insert({
            "title": bookName,
            "author": bookAuthor,
            "gender": bookGender.title(),
            "read": isRead
        }).execute()


def modifyBook():
    books = bookList().select("title", "author").execute().data
    print(books)
    bookName, bookAuthor = chooseBook(False)
    print({'title': bookName, 'author': bookAuthor})
    if {'title': bookName, 'author': bookAuthor} not in books:
        print("Le livre n'est pas dans la bibliothèque !")
        if input("Voulez vous en modifier un autre ? (oui/non) ").lower() == "oui":
            modifyBook()
    else:
        book = bookList().select("title", "author", "gender", "read").eq("title", bookName).eq("author", bookAuthor).execute().data
        book = book[0]
        while True:
            choice = input(f"Que voulez vous modifier sur {bookTitle(book["title"])}, {book["author"]},  {book["gender"]}, {"lu" if book["read"] else "pas lu"} ? (Nom, Auteur, Genre, Lu, Supprimer) ?\nChoix: ").lower()

            if choice == "nom":
                newName = input(f"Quel nouveau nom voulez vous donner à {bookTitle(book["title"])} de {book["author"]} ? ")
                book['title'] = newName
                bookList().update({"title": newName}).eq("title", bookName).eq("author", bookAuthor).execute().data
            elif choice == "auteur":
                newAuthor = input(f"Quel est le nouveau nom de l'auteur de {bookTitle(book["title"])} de {book["author"]} ? ")
                book['author'] = newAuthor
                bookList().update({"author":newAuthor}).eq("title", bookName).eq("author", bookAuthor).execute().data
            elif choice == "genre":
                newGender = input(f"Quel est le nouveau nom de l'auteur de {bookTitle(book["title"])} de {book["author"]}, {book["gender"]} ? ")
                book['gender'] = newGender
                bookList().update({"gender": newGender}).eq("title", bookName).eq("author", bookAuthor).execute().data
            elif choice == "lu":
                book["read"] = not book["read"]
                bookList().update({"read": book["read"]}).eq("title", bookName).eq("author", bookAuthor).execute().data
                print(f"Le livre est bien noté en {"lu" if book["read"] else "non lu"}")
            elif choice == "supprimer":
                delete = input(f"Etes vous sûr de vouloir supprimer {bookTitle(book['title'])} de {book['author']} ? (oui/non) ").lower() == "oui"
                if delete:
                    bookList().delete().eq("title", bookName).eq("author", bookAuthor).execute()
                    return
            else:
                print("Veuillez choisir une option valide !")
                continue

            choice = input("Voulez vous modifier quelque chose d'autre sur le livre ? (oui/non) ").lower()
            if choice == "non":
                break
            

def listBook():
    nbrOfBooks = len(bookList().select("read").execute().data)
    nbrReadBooks = len(bookList().select("read").eq("read", True).execute().data)
    print(f"\nVous avez lu {nbrReadBooks}/{nbrOfBooks} livres soit {100*nbrReadBooks/nbrOfBooks:.1f}% de votre bibliothèque.")
    choice = input("Vous voulez:\n1. Lister tout les livres\n2. Lister les livres par genre\n3. Lister les livres lus\n4. Lister les livres non lus\nChoix: ")
    books = bookList().select("title", "author", "gender", "read")
    while True: 
        if choice == "1":
            books = books.execute().data
            break
        elif choice == "2":
            genderChoice = input("Quel genre de livre voulez vous voir ? ").title()
            while genderChoice not in [i["gender"] for i in bookList().select("gender").execute().data]:
                genderChoice = input("Ce type de genre n'est pas présent, quel genre de livre voulez vous voir ? ")
            books = books.eq("gender", genderChoice).execute().data
            break
        elif choice == "3":
            books = books.eq("read", True).execute().data
            break
        elif choice == "4":
            books = books.eq("read", False).execute().data
            break
        else:
            print("Veuillez choisir une option valide !")
            
    print("\nVous avez:")
    books = sorted(books, key = lambda book : (book["author"].split(" ")[-1], book["title"]))
    for book in books:
        print(f"{bookTitle(book["title"])}, {book["author"]}, {book["gender"]}, {"lu" if book["read"] else "pas lu"}")


def putBook():
    bookName, bookAuthor = chooseBook(False)
    book = bookList().select("title", "author", "gender").eq("title", bookName).eq("author", bookAuthor).execute().data
    book = book[0]
    books = bookList().select("title", "author", "gender").eq("gender", book["gender"]).execute().data
    books = sorted(books, key = lambda book : (book["author"].split(" ")[-1], book["title"]))

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
        print(f"C'est le premier livre à mettre en {book["gender"].title()} ! Le livre après est {bookTitle(postBook['title'])} de {postBook['author']}")
    elif postBook == 0:
        print(f"C'est le dernier livre à mettre en {book["gender"].title()} ! Le livre avant est {bookTitle(preBook['title'])} de {preBook['author']}")
    else:
        if preBook['author'] == postBook['author']:
            print(f"Il faut ranger {bookTitle(book["title"])} entre {bookTitle(preBook['title'])} et {bookTitle(postBook['title'])} de {book['author']}")
        else:
            print(f"Il faut ranger {bookTitle(book["title"])} de {book['author']} entre {bookTitle(preBook['title'])} de {preBook['author']} et {bookTitle(postBook['title'])} de {postBook['author']}")

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[H\033[J", end="")

def menu():
    choice = input("\nQue voulez vous faire ?\n1. Ajouter un livre dans la bibliothèque\n2. Ranger un livre\n3. Lister les livres\n4. Modifier un livre\n5. Vider le terminal\n6. Quitter le programme\nChoix: ").lower()

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
        clear()
    elif choice == 6:
        exit()
    else:
        print("Veuillez choisir une option valide !")
        return menu()


while True:
    menu()
