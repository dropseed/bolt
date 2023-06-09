import os
import subprocess

import click

from ..utils import get_repo_root


@click.command("format")  # format is a keyword
@click.option("--check", is_flag=True, help="Check formatting instead of fixing")
@click.argument("files", nargs=-1)
def cli(check, files):
    """Format Python code with black and ruff"""
    if not files:
        repo_root = get_repo_root()
        # Make relative for nicer output
        files = [os.path.relpath(os.path.join(repo_root, "app"))]

    if check:
        fmt_check(files)
    else:
        fmt(files)


def fmt(files):
    # If we're fixing, we do ruff first so black can re-format any ruff fixes
    print_event(f"Fixing {', '.join(files)} with ruff")
    subprocess.check_call(
        [
            "ruff",
            "--fix-only",
            "--exit-zero",
            *files,
        ]
    )

    print_event(f"Formatting {', '.join(files)} with black")
    subprocess.check_call(
        [
            "black",
            *files,
        ]
    )


def fmt_check(files):
    print_event(f"Checking {', '.join(files)} with black")
    subprocess.check_call(["black", "--check", *files])

    print_event(f"Checking {', '.join(files)} with ruff")
    subprocess.check_call(["ruff", *files])


def print_event(msg, newline=True):
    arrow = click.style("-->", fg=214, bold=True)
    if not newline:
        message += " "
    click.secho(f"{arrow} {msg}", nl=newline)
