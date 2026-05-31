from typer import Typer

from .create import app as create_app

app = Typer(help="Manage GitHub issues.")
app.add_typer(create_app)
