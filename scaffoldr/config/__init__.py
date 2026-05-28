from typer import Context as typer_context
from typer import Typer

from scaffoldr.utils import check_legacy_config

from .init import app as init_app
from .migrate import app as migrate_app
from .show import app as show_app

app = Typer(help="Manage scaffoldr config.")
app.add_typer(init_app)
app.add_typer(show_app)
app.add_typer(migrate_app)


@app.callback()
def config_callback(ctx: typer_context):
    if ctx.invoked_subcommand == "migrate":
        return
    check_legacy_config()
