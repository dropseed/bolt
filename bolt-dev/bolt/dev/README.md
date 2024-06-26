# bolt-dev

A single command to run everything you need for local Bolt development.

![Bolt work command example](https://user-images.githubusercontent.com/649496/176533533-cfd44dc5-afe5-42af-8b5d-33a9fa23f8d9.gif)

The `bolt dev` command runs a combination of local commands + a Docker container for your database.

The following processes will run simultaneously (some will only run if they are detected as available):

<!-- - [`manage.py runserver` (and migrations)](#runserver)
- [`bolt-db start --logs`](#bolt-db)
- [`bolt-tailwind compile --watch`](#bolt-tailwind)
- [`npm run watch`](#package-json)
- [`stripe listen --forward-to`](#stripe)
- [`ngrok http --subdomain`](#ngrok)

It also comes with [debugging](#debugging) tools to make local debugging easier with VS Code. -->

## Installation

```sh
pip install bolt-dev
```

If you have `bolt-db` installed (i.e. you're using a database),
then add `DATABASE_URL` to your `.env` file.

```sh
DATABASE_URL=postgres://postgres:postgres@localhost:54321/postgres
```

```toml
# pyproject.toml
[tool.bolt.dev.services]
postgres = {cmd = "docker run --name app-postgres --rm -p 54321:5432 -v $(pwd)/.bolt/dev/pgdata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres postgres:15 postgres"}
```

```sh
bolt dev
```

## `bolt dev`

### Default processes

- bolt preflight
- gunicorn
- migrations
- tailwind

### Custom processes

- package.json "dev" script
- pyproject.toml `tool.bolt.dev.run = {command = "..."}`

### GitHub Codespaces

The `BASE_URL` setting is automatically set to the Codespace URL.

TODO

## `bolt dev db`

Only supports Postgres currently.

- snapshot
- import
- export


## Development processes

### Gunicorn

The key process here is still `manage.py runserver`.
But, before that runs, it will also wait for the database to be available and run `manage.py migrate`.

### bolt-db

If [`bolt-db`](https://github.com/boltpackages/bolt-db) is installed, it will automatically start and show the logs of the running database container.

### bolt-tailwind

If [`bolt-tailwind`](https://github.com/boltpackages/bolt-tailwind) is installed, it will automatically run the Tailwind `compile --watch` process.

## Debugging

[View on YouTube →](https://www.youtube.com/watch?v=pG0KaJSVyBw)

Since `bolt work` runs multiple processes at once, the regular [pdb](https://docs.python.org/3/library/pdb.html) debuggers can be hard to use.
Instead, we include [microsoft/debugpy](https://github.com/microsoft/debugpy) and an `attach` function to make it even easier to use VS Code's debugger.

First, import and run the `debug.attach()` function:

```python
class HomeView(TemplateView):
    template_name = "home.html"

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)

        # Make sure the debugger is attached (will need to be if runserver reloads)
        from bolt.work import debug; debug.attach()

        # Add a breakpoint (or use the gutter in VSCode to add one)
        breakpoint()

        return context
```

When you load the page, you'll see "Waiting for debugger to attach...".

Add a new VS Code debug configuration (using localhost and port 5768) by saving this to `.vscode/launch.json` or using the GUI:

```json
// .vscode/launch.json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Bolt: Attach to Django",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ],
            "justMyCode": true,
            "django": true
        }
    ]
}
```

Then in the "Run and Debug" tab, you can click the green arrow next to "Bolt: Attach to Django" to start the debugger.

In your terminal is should tell you it was attached, and when you hit a breakpoint you'll see the debugger information in VS Code.
If Django's runserver reloads, you'll be prompted to reattach by clicking the green arrow again.
