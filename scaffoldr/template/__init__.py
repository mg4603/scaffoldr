from typer import Typer

from .list import app as list_app
from .validate import app as validate_app

app = Typer(help="Manage scaffoldr templates.")
app.add_typer(list_app)
app.add_typer(validate_app)
