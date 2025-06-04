import os
import sys

import typer

from correspondence import models
from correspondence.main import app

cli = typer.Typer()


@cli.command()
def root():
    pass


@cli.command()
def shell():
    import IPython

    banner = "Python %s on %s\nIPython: %s\nApp: %s\n" % (
        sys.version,
        sys.platform,
        IPython.__version__,
        app.debug and " [debug]" or "",
    )

    ctx = {"app": app, "db": app.db}

    for k in models.__all__:
        ctx[k] = getattr(models, k)

    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup, "rb") as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    IPython.embed(banner1=banner, user_ns=ctx)


if __name__ == "__main__":
    cli()
