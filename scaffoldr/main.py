from __future__ import annotations

import typer

from scaffoldr.config import app as config_app
from scaffoldr.init import app as init_app
from scaffoldr.issues import app as issues_app
from scaffoldr.new import app as new_app
from scaffoldr.template import app as template_app
from scaffoldr.utils import check_legacy_config, ensure_dirs

app = typer.Typer(
    name="scaffoldr",
    help="Scaffold new projects with opinionated structure.",
    no_args_is_help=True,
)

app.add_typer(init_app)
app.add_typer(new_app)
app.add_typer(config_app, name="config")
app.add_typer(issues_app, name="issues")
app.add_typer(template_app, name="template")


@app.callback()
def app_callback(ctx: typer.Context):
    ensure_dirs()
    if ctx.invoked_subcommand == "config":
        return
    check_legacy_config()
