from textual.widgets import ContentSwitcher, Input, Label, Static, Button
from textual.containers import Horizontal, Container
from baseScreen import BaseScreen, mergeCSS
import books
import json


class LoginScreen(BaseScreen):
    CSS = mergeCSS("tcss/login/questionView.tcss", "tcss/login/yesView.tcss")


    def compose(self):
        yield from super().compose()

        yield ContentSwitcher(
            QuestionView(id="question"),
            YesView(id="yes"),
            NoView(id="no"),
            initial="question"
        )


class QuestionView(Container):
    def compose(self):
        yield from super().compose()
        yield Container(
            Static("""
   ▄▄▄                                                                          ▄▄    ▄▄                                                           
   ██▀▀█▄                                                                      ▄█▀▀█▄   ██                             █▄                           
   ██ ▄█▀ ▀▀       ▄                 ▄                               ▄         ██  ██   ██                    ▄        ██ ▄    ▀▀                   
   ██▀▀█▄ ██ ▄█▀█▄ ████▄▀█▄ ██▀▄█▀█▄ ████▄ ██ ██ ▄█▀█▄   ▄██▀█ ██ ██ ████▄     ██▀▀██   ██ ▄█▀█▄▀██ ██▀ ▄▀▀█▄ ████▄ ▄████ ████▄██ ▄█▀█▄             
 ▄ ██  ▄█ ██ ██▄█▀ ██ ██ ██▄██ ██▄█▀ ██ ██ ██ ██ ██▄█▀   ▀███▄ ██ ██ ██      ▄ ██  ██   ██ ██▄█▀  ███   ▄█▀██ ██ ██ ██ ██ ██   ██ ██▄█▀             
 ▀██████▀▄██▄▀█▄▄▄▄██ ▀█  ▀█▀ ▄▀█▄▄▄▄██ ▀█▄▀██▀█▄▀█▄▄▄  █▄▄██▀▄▀██▀█▄█▀      ▀██▀  ▀█▄█▄██▄▀█▄▄▄▄██ ██▄▄▀█▄██▄██ ▀█▄█▀███▄█▀  ▄██▄▀█▄▄▄             
                                                                                                                                                    
                                                                                                                                                    
                                                                                                                                                    
     ▄▄                                                                                                        ▄▄     ▄▄▄                    ▄▄▄▄▄  
   ▄█▀▀█▄                                                                                         █▄           ██▄   ██▀                    ██▀▀▀██ 
   ██  ██                                                      ▄                   ▄             ▄██▄          ███▄  ██             ▄          ▄██▀ 
   ██▀▀██ ▀█▄ ██▀▄█▀█▄ ▀▀▀██  ▀█▄ ██▀▄███▄ ██ ██ ▄██▀█   ██ ██ ████▄   ▄███▀ ▄███▄ ███▄███▄ ████▄ ██ ▄█▀█▄     ██ ▀█▄██ ▄█▀█▄ ▄███▄ ████▄     ██    
 ▄ ██  ██  ██▄██ ██▄█▀   ▄█▀   ██▄██ ██ ██ ██ ██ ▀███▄   ██ ██ ██ ██   ██    ██ ██ ██ ██ ██ ██ ██ ██ ██▄█▀     ██   ▀██ ██▄█▀ ██ ██ ██ ██           
 ▀██▀  ▀█▄█ ▀█▀ ▄▀█▄▄▄▄▄██▄▄    ▀█▀ ▄▀███▀▄▀██▀██▄▄██▀  ▄▀██▀█▄██ ▀█  ▄▀███▄▄▀███▀▄██ ██ ▀█▄████▀▄██▄▀█▄▄▄   ▀██▀    ██▄▀█▄▄▄▄▀███▀▄██ ▀█     ██    
                                                                                            ██                                                      
                                                                                            ▀                                                       
""", classes="question"),
            Horizontal(
                Button("Oui", variant="primary"),
                Button("Non", variant="error"),
                classes = "buttons",
            ),
            id = "dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.label == "Oui":
            self.query_ancestor(ContentSwitcher).current = "yes"
        else:
            self.query_ancestor(ContentSwitcher).current = "no"


class YesView(Container):
    def compose(self):
        yield from super().compose()
        yield Container(
            Label("[b]Veuillez mettre le lien de votre base de donnée Neon:[b]", classes="label"),
            Input(placeholder="Lien de la base de donnée (ex: postgresql://neondb_owner:*********@...)"),
            id = "inputDB"
        )

    def on_input_submitted(self, event: Input.Submitted):
        try:
            self.app.database = books.Database(event.value)
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            config["databaseUrl"] = event.value
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.app.switch_screen("main")
        except:
            event.input.value = ""
            event.input.placeholder = "Lien invalide ! Le debut doit être : postgresql://neondb_owner:*********@"


class NoView(Container):
    def compose(self):
        yield from super().compose()
        yield Static("No screen.")