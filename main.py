from textual.app import App
from pathlib import Path
import modeMainScreen
import modeLogin
import books
import json

configPath = Path("config.json")

try:
    with configPath.open("r", encoding="utf-8") as f:
        config = json.load(f)

except:
    config = {
        "databaseUrl": ""
    }

    with configPath.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


class Alexandrie(App):
    SCREENS = {
        "login": modeLogin.LoginScreen,
        "main": modeMainScreen.MainScreen
    }

    def on_mount(self):

        if config["databaseUrl"]:
            self.database = books.Database(config["databaseUrl"])
            self.push_screen("main")
        else:
            self.push_screen("login")


if __name__ == "__main__":
    app = Alexandrie()
    app.run()
