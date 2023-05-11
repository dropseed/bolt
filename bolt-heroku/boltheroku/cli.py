import os
import subprocess
import sys

import click

from .utils import generate_secret_key

BOLT_BUILDPACK = "https://github.com/dropseed/heroku-buildpack-bolt"


@click.group("heroku")
def cli():
    """Commands for deploying and managing Heroku apps"""
    pass


@cli.command()
@click.option("--postgres-tier", default="hobby-dev")
@click.option("--redis-tier", default="hobby-dev")
@click.option("--team", default="")
@click.argument("heroku_app_name")
@click.pass_context
def create(ctx, heroku_app_name, postgres_tier, redis_tier, team):
    """Create a new Heroku app with Postgres and Redis"""
    if (
        subprocess.call(
            ["git", "remote", "show", "heroku"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        == 0
    ):
        click.secho("heroku remote already exists", fg="red", err=True)
        sys.exit(1)

    if team:
        click.secho(f"Creating Heroku app on {team}", bold=True)
        subprocess.check_call(
            ["heroku", "apps:create", heroku_app_name, "--team", team]
        )
    else:
        click.secho("Creating Heroku app", bold=True)
        subprocess.check_call(["heroku", "apps:create", heroku_app_name])

    click.echo()
    ctx.invoke(set_buildpacks, confirm=True)
    click.echo()

    click.secho("Adding Postgres and Redis", bold=True)
    subprocess.check_call(
        ["heroku", "addons:create", f"heroku-postgresql:{postgres_tier}"]
    )
    click.echo()
    subprocess.check_call(["heroku", "addons:create", f"heroku-redis:{redis_tier}"])
    click.echo()

    click.secho("Setting SECRET_KEY and BASE_URL", bold=True)
    secret_key = generate_secret_key()
    # TODO --domain option?
    base_url = f"https://{heroku_app_name}.herokuapp.com"
    subprocess.check_call(
        [
            "heroku",
            "config:set",
            f"SECRET_KEY={secret_key}",
            f"BASE_URL={base_url}",
        ]
    )

    click.echo()
    click.secho("Enabling runtime-dyno-metadata", bold=True)
    subprocess.check_call(["heroku", "labs:enable", "runtime-dyno-metadata"])

    click.echo()
    click.secho(
        "Almost done! Next we'll make your first deploy using these steps:\n", bold=True
    )
    click.secho(
        "\n".join(
            [
                f"  1. Add and {click.style('git commit', bold=True)} any outstanding changes",
                f"  2. Manually {click.style('git push', bold=True)} to Heroku",
                f"  3. Prompt to {click.style('createsuperuser', bold=True)} on the production app",
            ]
        )
        + "\n"
    )

    if not click.confirm(click.style("Ready to commit and deploy?", bold=True)):
        click.secho(
            "Aborting. Your Heroku app is ready and you can deploy it yourself when you're ready!"
        )
        sys.exit(0)

    if subprocess.check_output(["git", "status", "--porcelain"]).strip():
        click.secho("\nYou have uncommitted changes.\n", fg="yellow")
        subprocess.check_call(["git", "status"])

        msg = click.prompt(
            "\n"
            + click.style(
                "Enter a commit message to add and commit them now", bold=True
            ),
            default="First commit",
        )
        subprocess.check_call(["git", "add", ".", "-A"])
        subprocess.check_call(["git", "commit", "-m", msg])

    branch_name = (
        subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        .decode("utf-8")
        .strip()
    )

    click.echo()
    click.secho(f"Pushing to Heroku with `git push heroku {branch_name}`", bold=True)
    subprocess.check_call(["git", "push", "heroku", branch_name])

    click.echo()
    click.secho("Running `createsuperuser` on the production app", bold=True)
    subprocess.check_call(["heroku", "run", "bolt", "django", "createsuperuser"])

    click.echo()
    click.secho(
        f"You're all set! You can connect your GitHub repo to the Heroku app at:\n\n  https://dashboard.heroku.com/apps/{heroku_app_name}/deploy/github",
        fg="green",
    )


@cli.command()
@click.option("--confirm", is_flag=True, default=False)
def set_buildpacks(confirm):
    """Automatically determine and set buildpacks"""
    buildpacks = [
        BOLT_BUILDPACK,
    ]

    try:
        repo_root = (
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError:
        click.secho(
            "All bolt projects are expected to be in a git repo and we couldn't find one.",
            fg="red",
        )
        exit(1)

    if os.path.exists(os.path.join(repo_root, "package.json")):
        buildpacks.append("heroku/nodejs")

    if os.path.exists(os.path.join(repo_root, "poetry.lock")):
        buildpacks.append(
            # TODO move to dropseed
            "https://github.com/forgepackages/heroku-buildpack-poetry"
        )

    buildpacks.append("heroku/python")

    click.secho("Suggested buildpacks:\n", bold=True)
    click.echo("\n".join([f"  {i+1}. {x}" for i, x in enumerate(buildpacks)]))

    if not confirm and not click.confirm(click.style("\nContinue?", bold=True)):
        return

    click.secho("\nSetting Heroku buildpacks", bold=True)
    subprocess.check_call(["heroku", "buildpacks:clear"])
    click.echo()

    for i, buildpack in enumerate(buildpacks):
        subprocess.check_call(
            ["heroku", "buildpacks:set", buildpack, "--index", str(i + 1)]
        )
        click.echo()


@cli.command()
def shell():
    """Open a remote Django shell"""
    subprocess.run(["heroku", "run", "bolt shell"])


@cli.command()
def serve():
    """Run a production server using gunicorn"""
    app_dir = os.path.join(os.getcwd(), "app")

    if os.path.exists(os.path.join(app_dir, "wsgi.py")):
        wsgi = "app.wsgi"
    else:
        wsgi = "bolt.wsgi.default"

    print(f"Using {wsgi} as WSGI entrypoint")

    result = subprocess.run(
        [
            "gunicorn",
            f"{wsgi}:application",
            "--log-file",
            "-",
        ],
        env={
            **os.environ,
            "PYTHONPATH": app_dir,
        },
    )
    sys.exit(result.returncode)


@cli.command("pre-deploy")
def pre_deploy():
    """Pre-deploy checks for release process"""
    click.secho("Running Django system checks", bold=True)
    subprocess.check_call(
        ["bolt", "django", "check", "--deploy", "--fail-level", "WARNING"]
    )

    click.echo()

    click.secho("Running Django migrations", bold=True)
    subprocess.check_call(["bolt", "django", "migrate"])

    click.echo()

    click.secho("Clearing expired sessions", bold=True)
    subprocess.check_call(["bolt", "django", "clearsessions"])


if __name__ == "__main__":
    cli()
