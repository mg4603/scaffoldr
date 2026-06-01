from typer import Typer

from .list import app as list_app

app = Typer(help="Manage scaffoldr templates.")
app.add_typer(list_app)
