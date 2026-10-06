from pathlib import Path

from textual.widgets import Header, Footer
from textual.screen import Screen

class BaseScreen(Screen):
    def compose(self):
        yield Header(show_clock=True)
        yield Footer()

    def on_mount(self):
        self.styles.background = "darkslategray"

def mergeCSS(*files):
    return "\n\n".join(Path(file).read_text(encoding="utf-8") for file in files)