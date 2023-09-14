import subprocess
import sys

import click

from bolt.db import DEFAULT_DB_ALIAS, connections


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--database",
    default=DEFAULT_DB_ALIAS,
    help=(
        "Nominates a database onto which to open a shell. Defaults to the "
        '"default" database.'
    ),
)
@click.argument("parameters", nargs=-1)
def shell(database, parameters):
    """Runs the command-line client for specified database, or the default database if none is provided."""
    connection = connections[database]
    try:
        connection.client.runshell(parameters)
    except FileNotFoundError:
        # Note that we're assuming the FileNotFoundError relates to the
        # command missing. It could be raised for some other reason, in
        # which case this error message would be inaccurate. Still, this
        # message catches the common case.
        click.secho(
            "You appear not to have the %r program installed or on your path."
            % connection.client.executable_name,
            fg="red",
            err=True,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        click.secho(
            '"%s" returned non-zero exit status %s.'
            % (
                " ".join(e.cmd),
                e.returncode,
            ),
            fg="red",
            err=True,
        )
        sys.exit(e.returncode)