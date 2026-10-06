from textual.widgets import Button, Checkbox, ContentSwitcher, Input, Static, Collapsible, DataTable
from textual.containers import Horizontal, Vertical, Container
from baseScreen import BaseScreen, mergeCSS
from textual.screen import ModalScreen
from textual import work
import requests

class MainScreen(BaseScreen):
    CSS = mergeCSS("tcss/main/mainView.tcss", "tcss/main/putBookScreen.tcss")

    def compose(self):
        yield from super().compose()

        yield ContentSwitcher(
            MainView(id="main"),
            SettingsView(id="settings"),
            StatView(id="stat"),
            initial="main"
        )




class MainView(Container):
    BINDINGS = [
        ("r", "putBook", "Ranger le livre sélectionné"),
        ("e", "modifyBook", "Modifier le livre sélectionné")
    ]

    def compose(self):
        yield Vertical(
            Horizontal(
                Collapsible(title="Livre en cours"),
                Input(placeholder="Rechercher un livre (@a auteur, @t titre du livre, @g genre, @r lu, @rr non lu)"),
                Button("", id="statsButton"),
                classes="upBar"
            ),

            Container(
                DataTable(),
                classes="tableContainer"
            ),

            Horizontal(
                Button("➕", id="addButton"),
                Static("", id="quote"),
                Button("Paramètres", id="settingsButton"),
                classes="downBar"
            )
        )

    def on_mount(self):
        self.database = self.app.database
        self.table = self.query_one(DataTable)

        self.initDatatable()

    def action_putBook(self):
        self.app.push_screen(PutBookScreen())

    @work
    async def action_modifyBook(self):
        if self.query_one(DataTable).cursor_row is not None:
            bookID, bookName, bookAuthor, bookGender, bookRead = self.query_one(DataTable).get_row_at(self.query_one(DataTable).cursor_row)
            if await self.app.push_screen_wait(BookScreen("modify", bookAuthor, bookName, bookGender, bookRead, bookID)):
                self.showBooks()


    @work
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "addButton":
            if await self.app.push_screen_wait(BookScreen(mode="new")):
                self.showBooks()

    def on_newBookClosed(self, result):
        if result:
            self.showBooks()

    @work(thread=True)
    def initDatatable(self):
        self.database.initializeCache()
        self.table.add_columns(*[("ID", "id"), ("Livre", "title"), ("Auteur", "author"), ("Genre", "gender"), ("Lu", "read")])
        self.table.zebra_stripes = True
        self.table.cell_padding = 2
        self.showBooks()
        self.get_quote()
        nbrOfBooks = len(self.database.bookList(self.database.cacheDB(), "read").fetchall())
        nbrReadBooks  = len(self.database.bookList(self.database.cacheDB(), "read", "WHERE read = ?", (True,)).fetchall())
        self.query_one("#statsButton", Button).label = f"Vous avez lu {nbrReadBooks }/{nbrOfBooks} livres soit {(100 * nbrReadBooks  / nbrOfBooks if nbrOfBooks else 0):.1f}%"

    def on_input_changed(self, event: Input.Submitted):
        self.table.clear()
        self.showBooks()

    @work(thread=True)
    def showBooks(self):
        inputChain = self.query_one(Input).value
        self.table.clear()
        books, nbrOfBooks, nbrReadBooks = self.database.listBook(inputChain=inputChain)
        self.query_one("#statsButton", Button).label = f"Vous avez lu {nbrReadBooks }/{nbrOfBooks} livres soit {(100 * nbrReadBooks  / nbrOfBooks if nbrOfBooks else 0):.1f}%"
        for book in books:
            self.table.add_row(*(book[0], book[1], book[2], book[3], "✔️" if book[4] else "❌"))

    @work(thread=True)
    def get_quote(self):
        while True:
            try:
                response = requests.get(
                    "https://zenquotes.io/api/today",
                    timeout=5
                )
                response.raise_for_status()

                data = response.json()[0]

                self.query_one("#quote").update(
                    f'"{data["q"]}"\n— {data["a"]}'
                )
                break

            except requests.RequestException:
                self.query_one("#quote").update(
                    "Impossible de récupérer la citation."
                )


class SettingsView(Container):
    def compose(self):
        yield Static("a")


class StatView(Container):
    def compose(self):
        yield Static("b")


class PutBookScreen(ModalScreen):
    CSS_PATH = "tcss/main/putBookScreen.tcss"
    BINDINGS = [
        ("escape", "close", "Fermer"),
        ("r", "close", "Fermer")
    ]

    def compose(self):
        yield Container(
            Static("Ranger les livres", id="putBook"),
            classes="putBook"
        )

    def action_close(self):
        self.dismiss()


class BookScreen(ModalScreen):
    CSS_PATH = "tcss/main/bookScreen.tcss"
    BINDINGS = [
        ("escape", "close", "Fermer"),
        ("enter", "submit", None),
    ]

    def __init__(self, mode, bookAuthor=None, bookName=None, bookGender=None, bookRead=None, bookID=None):
        super().__init__()
        self.mode = mode
        self.bookName = bookName
        self.bookAuthor = bookAuthor
        self.bookGender = bookGender
        self.bookRead = bookRead
        self.bookID = bookID

    def compose(self):
        delete = []
        if self.mode == "modify":
            delete.append(Button("Supprimer", classes="delete"))
        children = [
            Input(placeholder="Auteur", classes="author compo"),
            Input(placeholder="Livre", classes="title compo"),
            Input(placeholder="Genre", classes="gender compo"),
            Horizontal(Checkbox("Lu ?", classes="read"), *delete, classes="horizontal compo"),
        ]

        yield Vertical(*children, classes="dialog")

    def on_mount(self):
        if self.mode == "new":
            pass
        elif self.mode == "modify":
            self.query_one(".author", Input).value = self.bookAuthor
            self.query_one(".title", Input).value = self.bookName
            self.query_one(".gender", Input).value = self.bookGender
            self.query_one(".read", Checkbox).value = True if self.bookRead == "✔️" else False

    def on_input_submitted(self, event: Input.Submitted):
        self.action_submit()

    @work
    async def on_button_pressed(self):
        if await self.app.push_screen_wait(DeleteBook(self.bookName, self.bookAuthor, self.bookID)):
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_submit(self):
        bookAuthor = self.query_one(".author", Input).value.strip()
        bookName = self.query_one(".title", Input).value.strip()
        bookGender = self.query_one(".gender", Input).value.strip()
        bookRead = self.query_one(".read", Checkbox).value

        if (bookName == "") or (bookAuthor == "") or (bookGender == ""):
            self.notify("Le titre, l'auteur et le genre de l'oeuvre doivent être définis !", severity="error", timeout=5)
        else:
            if self.mode == "new":
                if bookAuthor and bookName and bookGender:
                    bookInDB = self.app.database.newBook(bookAuthor, bookName, bookGender, self.query_one(".read").value)
                    if bookInDB:
                        self.notify("Le livre est déjà dans la bibliothèque !", severity="error", timeout=5)
                    else:
                        self.notify(f"{bookName} de {bookAuthor} a bien été ajouté à la bibliothèque.", timeout=5)
                        self.dismiss(True)

            elif self.mode == "modify":
                self.app.database.modifyBook(bookName, bookAuthor, bookGender,  bookRead, self.bookID)
                self.notify(f"{bookName} de {bookAuthor} a bien été modifié.", timeout=5)
                self.dismiss(True)

    def action_close(self):
        self.dismiss(False)


class DeleteBook(ModalScreen):
    CSS_PATH = "tcss/main/deleteBook.tcss"
    BINDINGS = [("escape", "close", "Fermer")]

    def __init__(self, bookName, bookAuthor, bookID):
        super().__init__()

        self.bookName = bookName
        self.bookAuthor = bookAuthor
        self.bookID = int(bookID)

    def compose(self):
        yield Vertical(
            Static("Êtes vous sur de vouloir supprimer", id = "question"),
            Static("", id = "bookTitle"),
            Horizontal(
                Button("Oui", variant="success", id = "yesButton"),
                Button("Non", variant="error", id = "noButton")
            ),
            classes="dialog"
        )

    def on_mount(self):
        self.query_one("#bookTitle", Static).content = f"[i]{self.bookName}[/] de {self.bookAuthor}"

    def on_button_pressed(self, event:Button.Pressed):
        if event.button.id == "yesButton":
            self.app.database.deleteBook(self.bookID)
            self.notify(f"{self.bookName} de {self.bookAuthor} a bien été supprimé.")
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_close(self):
        self.dismiss(False)